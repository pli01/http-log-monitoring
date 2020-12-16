#!/usr/bin/env python3
import time
from datetime import datetime, tzinfo, timedelta
import random
import argparse


def generate_log_line():
    ips = ["127.0.0.1", "10.1.1.1", "192.168.1.1"]
    users = ["james", "jill", "frank", "mary"]
    resources = ["/report", "/api/user", "/"]
    methods = ["GET", "POST", "PUT"]
    status_code = [200, 503, 302, 404]

    otime = datetime(2020, 12, 12)

    increment = timedelta(seconds=random.randint(30, 300))
    otime += increment
    timestamp = otime.strftime('%d/%b/%Y:%H:%M:%S')+' +0000'
    ip = random.choice(ips)
    user = random.choice(users)
    method = random.choice(methods)
    uri = random.choice(resources)
    status = random.choice(status_code)
    size = str(random.randrange(2000, 5000))
    return '{} - {} [{}] "{} {} HTTP/1.0" {} {}\n'.format(ip, user, timestamp, method, uri, status, size)


def main(filename, threshold, duration):
    print('Append {} random log line per second during {} seconds in {} '.format(
        threshold, duration, filename))

    f = open(filename, 'a')

    for t in range(0, duration):
        for i in range(0, threshold):
            f.write(generate_log_line())
        print("{} {}/{}s write {} req/s".format(datetime.now()
                                                .strftime('%Y-%m-%d %H:%M:%S'), t, duration, threshold))
        f.flush()
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP log generator')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?',
                        default='/tmp/access.log', help='http log file (default: /tmp/access.log)')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int,
                        default=10, help='threshold (default: 10 req per second)')
    parser.add_argument('-d', '--duration', metavar='duration',
                        type=int, default=10, help='duration (default: 10s)')
    args = parser.parse_args()

    try:
        print(__file__, "generate log in file", args.filename)
        main(args.filename, args.threshold, args.duration)
    except KeyboardInterrupt:
        print(__file__, "stopped")
