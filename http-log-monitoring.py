#!/usr/bin/env python3
import re
import datetime
import time, os, sys
from collections import Counter
import argparse

def alarm_threshold(now,alarm_total_req_count,threshold,ALERT_INTERVAL,alert):
    """
    Alarm threshold: Display alert when total traffic for the past X minutes exceeds a certain number on average (threshold req/s)
      return True|False
    """
    average = alarm_total_req_count/ALERT_INTERVAL
    if not alert and average >= threshold:
       print("High traffic generated an alert - hits = {value}, triggered at {time}".format(value=average,time=display_time(now)))
       alert = True
    elif alert and average < threshold:
       print("Traffic back to normal - hits = {value}, recovered at {time}".format(value=average,time=display_time(now)))
       alert = False
    return alert

def display_stats(now,total_req_count, STATS_INTERVAL, stats_data, alarm_total_req_count, ALERT_INTERVAL):
    """
    Display stats about the traffic during X s
    """
    average = total_req_count / STATS_INTERVAL
    print("{time} Summary stats last {count} seconds: {total} req / {count} seconds - {average}/s - {alert_average}/s".format(time=display_time(now), total=total_req_count,count=STATS_INTERVAL,average=average, alert_average=(alarm_total_req_count/ ALERT_INTERVAL)))
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
               count.append('{key} ({count} times)'.format(key=x[0], count=x[1]))
           string += '{title}: {count}\n'.format(title=k, count=', '.join(count))
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
    alarm_total_req_count = 0
    alert = False
    stats_data = {}

    now = time.time()
    statsTime = now + STATS_INTERVAL
    alertTime = now + ALERT_INTERVAL

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
            alarm_total_req_count += 1
        else:
            file.seek(pos)
        if now >= statsTime:
            display_stats(now,total_req_count, STATS_INTERVAL, stats_data, alarm_total_req_count, ALERT_INTERVAL)
            total_req_count = 0
            stats_data = {}
            statsTime = now + STATS_INTERVAL
        if now >= alertTime:
            alert = alarm_threshold(now,alarm_total_req_count,threshold,ALERT_INTERVAL,alert)
            alarm_total_req_count = 0
            alertTime = now + ALERT_INTERVAL

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP log monitoring console program')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?', default = '/tmp/access.log', help='http log file (default: /tmp/access.log)')
    parser.add_argument('-s', '--stats', metavar='stats', type=int, default = 10, help='statistics interval (default: 10s)')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int, default = 10, help='threshold used by 2 minutes alarms (default: 10 req/s)')
    parser.add_argument('-a', '--alarm', metavar='alarm', type=int, default = 180, help='alarm interval (default: 180s)')
    args = parser.parse_args()

    try:
        print("{progname} watch log file {filename}".format(progname=__file__,filename=args.filename))
        main(args.filename, args.stats, args.threshold, args.alarm)
    except KeyboardInterrupt:
        print("{progname} stopped".format(progname=__file__))
