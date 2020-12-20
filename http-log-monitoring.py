#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   HTTP log monitoring console program
   Read log file "filename" , display stats at regular interval, and display alert when threshold is exceeded
"""

import argparse
import datetime
import os
import re
import sys
import time
from collections import Counter


def r_average(elt, count):
    """
    Return rounded average
    """
    return round(elt / count, 1)


def alarm_threshold(now, alarm_total_req_count, alert_interval, threshold, alert_sent):
    """
    Display alert when total traffic for the past X minutes exceeds a certain number on average (threshold req/s)
    """
    average = r_average(alarm_total_req_count, alert_interval)
    if average >= threshold and not alert_sent:
        print('High traffic generated an alert - hits = {value}, triggered at {time}'.format(
            value=average, time=display_time(now)))
        alert_sent = True
    elif average < threshold and alert_sent:
        print('Traffic back to normal - hits = {value}, recovered at {time}'.format(
            value=average, time=display_time(now)))
        alert_sent = False
    return alert_sent


def display_summary_stats(now, stats_interval, stats_data):
    """
    Display interesting summary statistics: section, host, authuser, status, request_method
    """
    total_req_count = 0
    size_bytes = 0
    summary = ''
    top = 3
    if len(stats_data) > 0:
        count = []
        summary = '\n'
        total_req_count = sum(Counter(stats_data['section']).values())
        size_bytes = sum(Counter(stats_data['size'].values()))

        for element in Counter(stats_data['section']).most_common(top):
            count.append('{key} = {count}'.format(
                key=element[0], count=element[1]))
        number = len(Counter(stats_data['section']))
        summary += '  Top {top} of total {number} web site "sections", most common : {count}'.format(
            top=top, number=number, count=', '.join(count))

        for field in ['host', 'authuser', 'status', 'request_method']:
            count = []
            summary += '\n'
            for element in Counter(stats_data[field]).most_common(top):
                count.append('"{key}" = {count}'.format(
                    key=element[0], count=element[1]))
            number = len(Counter(stats_data[field]))
            summary += '  Most common of {number} "{title}" : {count}'.format(
                title=field, number=number, count=', '.join(count))

    average = r_average(total_req_count, stats_interval)

    string = '{time} Summary stats last {count} seconds:' \
             'hits = {total} - average = {average}/s - size = {size_bytes} bytes'.format(
                 time=display_time(now), count=stats_interval, total=total_req_count, average=average,
                 size_bytes=size_bytes)

    print(string + summary)


def display_time(timestamp):
    """
    Return formatted display timestamp
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def parse_clf_http_line(line, stats_data):
    """
    Parse line in the common log format (https://en.wikipedia.org/wiki/Common_Log_Format)
    example:
      127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
    use Regex to split in

    Returns:
       Generate a dictionary from the CLF log entry
    """
    pattern = re.compile(
        r'^(?P<host>\S*)'  # host
        r' (?P<ident>\S*)'  # ident
        r' (?P<authuser>\S*)'  # authuser
        r' \[(?P<date>.*?)\]'  # date
        r' \"(?P<request_method>.*?)'  # request_method
        r' (?P<path>.*?)'  # path
        r'(?P<request_version> HTTP/.*)?\"'  # request_version
        r' (?P<status>\d*)'  # status
        r' (?P<size>\d*)$'  # size
    )

    try:
        data = pattern.match(line).groupdict()

        # split section path
        path_components = os.path.normpath(data['path']).split('/')
        section = '/'
        if path_components[1]:
            section = section + path_components[1]

        # update entry in dict counter
        entry = [
            ('section', section),
            ('host', data['host']),
            ('authuser', data['authuser']),
            ('request_method', data['request_method']),
            ('status', data['status']),
            ('size', data['size'])
        ]
        for key, value in entry:
            if key not in stats_data:
                stats_data[key] = Counter()
            if key == 'size':  # increment total bytes size
                stats_data[key].update({key: int(data['size'])})
            else:
                stats_data[key].update([value])
    except:  # skip log line if not in CLF format
        pass

    return stats_data


def main(filename, stats_interval, threshold, alarm_interval):
    stats_timer = 0
    alarm_timer = 0
    total_req_count = 0
    alarm_total_req_count = 0
    alert_sent = False
    stats_data = {}

    seek_end = True
    while True:
        try:  # open the file for reading
            with open(filename, 'r') as file:
                if seek_end:  # reopened files must not seek end
                    file.seek(0, os.SEEK_END)  # shift at the end of file
                while True:  # line reading loop
                    now = time.time()
                    line = file.readline()
                    if line:
                        stats_data = parse_clf_http_line(line, stats_data)
                        total_req_count += 1
                        continue

                    try:
                        if file.tell() > os.path.getsize(filename):  # rotation occurred (copytruncate/create)
                            file.close()
                            seek_end = False
                            break
                        pos = file.tell()
                        file.seek(pos)
                        time.sleep(1)
                        stats_timer += 1
                        alarm_timer += 1

                        if stats_timer == stats_interval:
                            display_summary_stats(
                                now, stats_interval, stats_data)
                            alarm_total_req_count += total_req_count
                            stats_data = {}
                            total_req_count = 0
                            stats_timer = 0

                        if alarm_timer == alarm_interval:
                            alert_sent = alarm_threshold(
                                now, alarm_total_req_count, alarm_interval, threshold, alert_sent)
                            alarm_total_req_count = 0
                            alarm_timer = 0

                    except FileNotFoundError:  # rotation occurred but new file still not created
                        print('{filename} is still not ready for reading'.format(
                            filename=filename))
                        time.sleep(1)

        except IOError:
            print('Unable to open {filename} for reading'.format(
                filename=filename))
            sys.exit(1)


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
        print('Starting {progname} reading log file {filename}'.format(
            progname=__file__, filename=args.filename))
        main(args.filename, args.stats, args.threshold, args.alarm)
    except KeyboardInterrupt:
        print('{progname} stopped'.format(progname=__file__))
