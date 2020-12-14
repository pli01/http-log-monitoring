#!/usr/bin/env python3
import re
import datetime
import time, os, sys
from collections import Counter
import argparse

"""
Default parameters:
  STATS_INTERVAL: Display stats every 10s
  ALERT_INTERVAL: Alert last 2mn (120s)
"""
# TODO: override parameters via config file or args
STATS_INTERVAL   = 10
ALERT_INTERVAL   = 120

def display_summary_stats(stats_data):
    """
    Display summary statistics
       section, host, authuser, status, request_method
    """
    if len(stats_data):
       for k in [ 'section', 'host', 'authuser', 'status', 'request_method' ]:
           for x in Counter(stats_data[k]).most_common(3):
               print('     {title} {key} : {count} times'.format(title=k,key=x[0], count=x[1]))

def display_time(time):
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

def parse_clf_http_line(line,stats_data):
    """
    Regex for the common log format (https://en.wikipedia.org/wiki/Common_Log_Format)
      host ident authuser date "request" status bytes
        with "request" as "method path request_version"
    example:
      127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326

    Generate a dictionary from the CLF log line
    """
    # TODO: catch AttributeError exception if error
    pattern = re.compile(
            r'^(?P<host>\S*)'             # host
            r' (?P<ident>\S*)'            # ident
            r' (?P<authuser>\S*)'         # authuser
            r' \[(?P<date>.*?)\]'         # date
            r' \"(?P<request_method>.*?)' # request_method
            r' (?P<path>.*?)'             # path
            r'(?P<request_version> HTTP/.*)?\"' # request_version
            r' (?P<status>\d*)'          # status
            r' (?P<bytes>\d*)$'          # bytes
        )

    data = pattern.match(line).groupdict()
    host           = data["host"]
    authuser       = data["authuser"]
    request_method = data["request_method"]
    path           = data["path"]
    status         = data["status"]
    bytes          = data["bytes"]

    # split section path
    path_components = os.path.normpath(path).split("/")
    section = "/"
    if path_components[1]:
        section = section + path_components[1]

    # store nested dict
    entry = [ ("section", section ), ("host", host), ("authuser", authuser), ("request_method", request_method) , ("status", status) ]
    for key, value in entry:
       if key in stats_data and value in stats_data[key]:
          stats_data[key][value] += 1
       elif key in stats_data:
          stats_data[key][value] = 1
       else:
          stats_data[key] = { value:  1 }

def main(filename,threshold):
    total_req_count = 0
    alarm_total_req_count = 0
    alert = False
    stats_data = {}

    now = time.time()
    statsTime = now + STATS_INTERVAL
    alertTime = now + ALERT_INTERVAL

    # open the file for reading and shift at the end of file
    try:
        file = open(filename, 'r')
    except IOError:
         print('Unable to open {filename} for reading'.format(filename=filename))
         sys.exit(1)

    file.seek(0, os.SEEK_END)

    while True:
        now = time.time()
        pos = file.tell()
        line = file.readline()
        if line:
            parse_clf_http_line(line,stats_data)
            total_req_count += 1
            alarm_total_req_count += 1
        else:
            file.seek(pos)
        if now >= statsTime:
            average = total_req_count / STATS_INTERVAL
            print("{time} Summary stats last {count} seconds: {total} req / {count} seconds - {average}/s - {alert_average}/s".format(time=display_time(now), total=total_req_count,count=STATS_INTERVAL,average=average, alert_average=(alarm_total_req_count/ ALERT_INTERVAL)))
            display_summary_stats(stats_data)
            total_req_count = 0
            stats_data = {}
            now = time.time()
            statsTime = now + STATS_INTERVAL
        if now >= alertTime:
            average = alarm_total_req_count/ALERT_INTERVAL
            if not alert and average >= threshold:
                print("High traffic generated an alert - hits = {value}, triggered at {time}".format(value=average,time=display_time(now)))
                alert = True
            elif alert and average < threshold:
                print("Traffic back to normal - hits = {value}, recovered at {time}".format(value=average,time=display_time(now)))
                alert = False
            alarm_total_req_count = 0
            now = time.time()
            alertTime = now + ALERT_INTERVAL

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP log monitoring console program')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?', default = '/tmp/access.log', help='http log file (default: /tmp/access.log)')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int, default = 10, help='threshold used by 2 minutes alarms (default: 10)')
    args = parser.parse_args()

    try:
        print("{progname} watch log file {filename}".format(progname=__file__,filename=args.filename))
        main(args.filename, args.threshold)
    except KeyboardInterrupt:
        print("{progname} stopped".format(progname=__file__))
