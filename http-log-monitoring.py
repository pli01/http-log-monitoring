#!/usr/bin/env python3
import re
import datetime
import time, os
from collections import Counter
import argparse

"""
Default parameters:
  STATS_INTERVAL: Display stats every 10s
  ALERT_INTERVAL: Alert last 2mn (120s)
"""
# TODO: override parameters via config file or args
STATS_INTERVAL   = 10
ALERT_INTERVAL   = 30

def display_summary_stats(result, stats_data):
    """
    Display summary statistics
    """
    total = sum(result)
    count = len(result)
    average = total / count
    print("Summary stats last {count} seconds: {total} req / {count} seconds - {average}/s".format(total=total,count=count,average=average))
    if len(stats_data):
       for k in [ 'section', 'host', 'authuser', 'status', 'request_method' ]:
           for x in Counter(stats_data[k]).most_common(5):
               print('     {title} {key} : {count} times'.format(title=k,key=x[0], count=x[1]))

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

    # nested dict
    entry = [ ("section", section ), ("host", host), ("authuser", authuser), ("request_method", request_method) , ("status", status) ]
    for key, value in entry:
       if key in stats_data and value in stats_data[key]:
          stats_data[key][value] += 1
       elif key in stats_data:
          stats_data[key][value] = 1
       else:
          stats_data[key] = { value:  1}

def main(filename,threshold):
    """
    Read log file, display stats, and alert
    """
    # TODO: parse args
    # TODO: catch error

    stats_result = []
    alert_result = []
    alert_generated = 0
    total_req_count = 0
    stat_count = 0
    alert_count = 0
    stats_data = {}

    # open the file for reading and shift at the end of file
    file = open(filename, 'r')
    file.seek(0, os.SEEK_END)

    while True:
        # read a single line
        pos = file.tell()
        line = file.readline()
        if not line:
            # store req / s
            # print("#", total_req_count, stat_count, alert_count, stats_result)
            stats_result.append(total_req_count)
            total_req_count=0
            stat_count += 1

            if stat_count == STATS_INTERVAL:
               display_summary_stats(stats_result, stats_data)
               alert_count += stat_count
               stat_count = 0
               stats_data = {}
               alert_result.extend(stats_result)
               stats_result.clear()

            if alert_count == ALERT_INTERVAL:
               now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
               average = 0
               if len(alert_result):
                  average = int(sum(alert_result) / len(alert_result))
               if average > threshold and not alert_generated:
                  print("High traffic generated an alert - hits = {value}, triggered at {time}".format(value=average,time=now))
                  alert_generated += 1
               elif alert_generated > 0:
                  print("Traffic back to normal - hits = {value}, recovered at {time}".format(value=average,time=now))
                  alert_generated = 0

               # reset
               alert_count = 0
               alert_result.clear()

            time.sleep(1)
            file.seek(pos)

        else:
          parse_clf_http_line(line,stats_data)
          total_req_count += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP log monitoring console program')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?', default = '/tmp/access.log', help='http log file')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int, default = 10, help='threshold used by 2 minutes alarms')
    args = parser.parse_args()

    try:
        print(__file__, "watch file",args.filename)
        main(args.filename, args.threshold)
    except KeyboardInterrupt:
        print(__file__, "stopped")
