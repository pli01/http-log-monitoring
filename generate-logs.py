#!/usr/bin/env python3
import time
from datetime import datetime, tzinfo, timedelta
import random
import argparse

def main(filename,threshold,duration):
    ips         = [ "127.0.0.1","10.1.1.1","192.168.1.1" ]
    users       = [ "james","jill","frank","mary" ]
    resources   = [ "/report","/api/user", "/" ]
    methods     = [ "GET","POST","PUT" ]
    status_code = [ 200, 503, 302,404 ]

    otime = datetime(2020,12,12)

    print('Append {} random logs in {} '.format(threshold, filename))

    f = open(filename,'a')

    for t in range(0,duration):
        for i in range(0,threshold):
            increment = timedelta(seconds=random.randint(30,300))
            otime += increment
            timestamp = otime.strftime('%d/%b/%Y:%H:%M:%S')+' +0000'
            ip = random.choice(ips)
            user = random.choice(users)
            method = random.choice(methods)
            uri = random.choice(resources)
            status = random.choice(status_code)
            size = str(random.randrange(2000,5000))
            f.write('{} - {} [{}] "{} {} HTTP/1.0" {} {}\n'.format( ip,user,timestamp, method, uri, status, size ))
            f.flush()
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP log generator')
    parser.add_argument('-f', '--filename', metavar='http log files', nargs='?', default = '/tmp/access.log', help='http log file (default: /tmp/access.log)')
    parser.add_argument('-t', '--threshold', metavar='threshold', type=int, default = 10, help='threshold (default: 10 req per second)')
    parser.add_argument('-d', '--duration', metavar='duration', type=int, default = 10, help='duration (default: 10s)')
    args = parser.parse_args()

    try:
        print(__file__, "generate log in file",args.filename)
        main(args.filename, args.threshold, args.duration)
    except KeyboardInterrupt:
        print(__file__, "stopped")
