#!/usr/bin/env python3
import re
import datetime
import time, os, sys
from collections import Counter
import argparse

def f_average(lst):
    return round( sum(lst) / len(lst) , 2)

def alarm_threshold(now,alarm_interval,threshold,alert):
    """
    Alarm threshold: Display alert when total traffic for the past X minutes exceeds a certain number on average (threshold req/s)
      return True|False
    """
    average = f_average(alarm_interval)
    if not alert and average >= threshold:
       print("High traffic generated an alert - hits = {value}, triggered at {time}".format(value=average,time=display_time(now)))
       alert = True
    elif alert and average < threshold:
       print("Traffic back to normal - hits = {value}, recovered at {time}".format(value=average,time=display_time(now)))
       alert = False
    return alert

def display_stats(now,stats_interval, stats_data):
    """
    Display stats about the traffic during X s
    """
    total = sum(stats_interval)
    count = len(stats_interval)
    average = f_average(stats_interval)
    print("{time} Summary stats last {count} seconds: hits = {total} - average = {average}/s".format(time=display_time(now), total=total,count=count,average=average))
    display_summary_stats(stats_data)

def display_summary_stats(stats_data):
    """
    Display interesting summary statistics
       section, host, authuser, status, request_method
    """
    if len(stats_data):
       string=""
       for k in [ 'section', 'host', 'authuser', 'status', 'request_method' ]:
           count = []
           for x in Counter(stats_data[k]).most_common(3):
               count.append('{key} = {count}'.format(key=x[0], count=x[1]))
           string += '  {title} hits: {count}\n'.format(title=k, count=', '.join(count))
       print(string)

def display_time(time):
    """
    Format display time
    """
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

def parse_clf_http_line(line,stats_data):
    """
    Parse line in the common log format (https://en.wikipedia.org/wiki/Common_Log_Format)
    use Regex to split in
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

def main(filename,stats,threshold,alarm):
    STATS_INTERVAL = stats
    ALERT_INTERVAL = alarm
    total_req_count = 0
    stats_interval = []
    alarm_interval = []
    alert = False
    stats_data = {}

    now = time.time()

    # open the file for reading
    try:
        file = open(filename, 'r')
    except IOError:
         print('Unable to open {filename} for reading'.format(filename=filename))
         sys.exit(1)
    # shift at the end of file
    file.seek(0, os.SEEK_END)

    while True:
        now = time.time()
        pos = file.tell()
        line = file.readline()
        if line:
            parse_clf_http_line(line,stats_data)
            total_req_count += 1
        else:
            file.seek(pos)
            time.sleep(1)

            stats_interval.append(total_req_count)
            total_req_count = 0

            if len(stats_interval) == STATS_INTERVAL:
                display_stats(now,stats_interval, stats_data)
                alarm_interval.append(sum(stats_interval))
                stats_data = {}
                stats_interval.clear()

            if len(alarm_interval) == (ALERT_INTERVAL/STATS_INTERVAL):
                alert = alarm_threshold(now,alarm_interval,threshold,alert)
                alarm_interval.clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP log monitoring console program')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?', default = '/tmp/access.log', help='http log file (default: /tmp/access.log)')
    parser.add_argument('-s', '--stats', metavar='stats', type=int, default = 10, help='statistics interval in second (default: 10)')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int, default = 10, help='threshold used by alarms in request/s (default: 10)')
    parser.add_argument('-a', '--alarm', metavar='alarm', type=int, default = 180, help='alarm interval in second (default: 180)')
    args = parser.parse_args()

    try:
        print("Starting {progname} reading log file {filename}".format(progname=__file__,filename=args.filename))
        main(args.filename, args.stats, args.threshold, args.alarm)
    except KeyboardInterrupt:
        print("{progname} stopped".format(progname=__file__))
