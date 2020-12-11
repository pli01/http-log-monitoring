#!/usr/bin/env python3
import time
from datetime import datetime, tzinfo, timedelta
import random
timestr = time.strftime("%Y%m%d-%H%M%S")
filename = "access_log_generated.log"

f = open(filename,'a')
MAX_LOG = 500

ips         = ["127.0.0.1","10.1.1.1","192.168.1.1"]
users       = ["james","jill","frank","mary"]
resources   = ["/report","/api/user", "/"]
methods     = ["GET","POST"]
status_code = [ 200, 503, 302 ]

otime = datetime(2020,12,12)

print('Append {} random logs in {} '.format(MAX_LOG, filename))

for i in range(0,MAX_LOG):
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
