#!/usr/bin/env python3
import re
import datetime
import time
import os
import sys
from collections import Counter
import argparse


def f_average(elt, count):
    return round(elt / count, 1)


def alarm_threshold(now, alarm_total_req_count, alert_interval, threshold, alert_sent):
    """
    Alarm threshold: Display alert when total traffic for the past X minutes exceeds a certain number on average (threshold req/s)
    """
    average = f_average(alarm_total_req_count, alert_interval)
    if average >= threshold and not alert_sent:
        print("High traffic generated an alert - hits = {value}, triggered at {time}".format(
            value=average, time=display_time(now)))
        alert_sent = True
    elif average < threshold and alert_sent:
        print("Traffic back to normal - hits = {value}, recovered at {time}".format(
            value=average, time=display_time(now)))
        alert_sent = False
    return alert_sent


def display_summary_stats(now, stats_interval, stats_data):
    """
    Display interesting summary statistics: section, host, authuser, status, request_method
    """
    total_req_count = 0
    size_bytes = 0
    summary = ""
    if len(stats_data):
        count = []
        summary = "\n"
        total_req_count = sum(Counter(stats_data['section']).values())
        size_bytes = sum(Counter(stats_data['size'].values()))

        for x in Counter(stats_data['section']).most_common(3):
            count.append('{key} = {count}'.format(key=x[0], count=x[1]))
        n = len(Counter(stats_data['section']))
        summary += '  total "sections" of the web site = {n} , most hits: {count}'.format(
            n=n, count=', '.join(count))

        for k in ['host', 'authuser', 'status', 'request_method']:
            count = []
            summary += '\n'
            for x in Counter(stats_data[k]).most_common(3):
                count.append('"{key}" = {count}'.format(key=x[0], count=x[1]))
            l = len(Counter(stats_data[k]))
            summary += '  most common of {l} "{title}" : {count}'.format(
                title=k, l=l, count=', '.join(count))

    average = f_average(total_req_count, stats_interval)

    string = "{time} Summary stats last {count} seconds: hits = {total} - average = {average}/s - size = {size_bytes} bytes".format(
        time=display_time(now), total=total_req_count, count=stats_interval, average=average, size_bytes=size_bytes)

    print(string + summary)


def display_time(time):
    """
    Format display time
    """
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')


def parse_clf_http_line(line, stats_data):
    """
    Parse line in the common log format (https://en.wikipedia.org/wiki/Common_Log_Format)
    example:
      127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
    use Regex to split in
      host ident authuser date "request" status size
        with "request" as "method path request_version"

    Generate a dictionary from the CLF log line
    """
    # TODO: catch AttributeError exception if error
    pattern = re.compile(
        r'^(?P<host>\S*)'             # host
        r' (?P<ident>\S*)'            # ident
        r' (?P<authuser>\S*)'         # authuser
        r' \[(?P<date>.*?)\]'         # date
        r' \"(?P<request_method>.*?)'  # request_method
        r' (?P<path>.*?)'             # path
        r'(?P<request_version> HTTP/.*)?\"'  # request_version
        r' (?P<status>\d*)'           # status
        r' (?P<size>\d*)$'            # size
    )

    data = pattern.match(line).groupdict()
    host = data["host"]
    authuser = data["authuser"]
    request_method = data["request_method"]
    path = data["path"]
    status = data["status"]
    size = data["size"]

    # split section path
    path_components = os.path.normpath(path).split("/")
    section = "/"
    if path_components[1]:
        section = section + path_components[1]

    # update dict counter
    entry = [("section", section), ("host", host), ("authuser", authuser),
             ("request_method", request_method), ("status", status)]
    for key, value in entry:
        if not key in stats_data:
            stats_data[key] = Counter()
        stats_data[key].update([value])
    # bytes size
    key = 'size'
    if not key in stats_data:
        stats_data[key] = Counter()
    stats_data[key].update({key: int(size)})

    return stats_data


def main(filename, stats_interval, threshold, alarm_interval):
    stats_timer = 0
    alarm_timer = 0
    total_req_count = 0
    alarm_total_req_count = 0
    alert_sent = False
    stats_data = {}
    now = time.time()

    # open the file for reading
    try:
        file = open(filename, 'r')
    except IOError:
        print('Unable to open {filename} for reading'.format(
            filename=filename))
        sys.exit(1)
    # shift at the end of file
    file.seek(0, os.SEEK_END)

    while True:
        now = time.time()
        pos = file.tell()
        line = file.readline()
        if line:
            stats_data = parse_clf_http_line(line, stats_data)
            total_req_count += 1
        else:
            file.seek(pos)
            time.sleep(1)
            stats_timer += 1
            alarm_timer += 1

            if stats_timer == stats_interval:
                display_summary_stats(now, stats_interval, stats_data)
                alarm_total_req_count += total_req_count
                stats_data = {}
                total_req_count = 0
                stats_timer = 0

            if alarm_timer == alarm_interval:
                alert_sent = alarm_threshold(
                    now, alarm_total_req_count, alarm_interval, threshold, alert_sent)
                alarm_total_req_count = 0
                alarm_timer = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='HTTP log monitoring console program')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?',
                        default='/tmp/access.log', help='http log file (default: /tmp/access.log)')
    parser.add_argument('-s', '--stats', metavar='stats', type=int,
                        default=10, help='statistics interval in second (default: 10)')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int,
                        default=10, help='threshold used by alarms in request/s (default: 10)')
    parser.add_argument('-a', '--alarm', metavar='alarm', type=int,
                        default=180, help='alarm interval in second (default: 180)')
    args = parser.parse_args()

    try:
        print("Starting {progname} reading log file {filename}".format(
            progname=__file__, filename=args.filename))
        main(args.filename, args.stats, args.threshold, args.alarm)
    except KeyboardInterrupt:
        print("{progname} stopped".format(progname=__file__))
