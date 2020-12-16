#  HTTP log monitoring console program

At Datadog, we value working on real solutions to real problems, and as such we think the best way to understand your capabilities is to give you the opportunity to solve a problem similar to the ones we solve on a daily basis. We ask that you write a simple console program that monitors HTTP traffic on your machine. Treat this as an opportunity to show us how you would write something you would be proud to put your name on.

* Consume an actively written-to CLF HTTP access log (https://en.wikipedia.org/wiki/Common_Log_Format). It should default to reading /tmp/access.log and be overrideable

Example log lines:
```
127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 200 123
127.0.0.1 - jill [09/May/2018:16:00:41 +0000] "GET /api/user HTTP/1.0" 200 234
127.0.0.1 - frank [09/May/2018:16:00:42 +0000] "POST /api/user HTTP/1.0" 200 34
127.0.0.1 - mary [09/May/2018:16:00:42 +0000] "POST /api/user HTTP/1.0" 503 12
```

* Display stats every 10s about the traffic during those 10s: the sections of the web site with the most hits, as well as interesting summary statistics on the traffic as a whole. A section is defined as being what's before the second '/' in the resource section of the log line. For example, the section for "/pages/create" is "/pages"
* Make sure a user can keep the app running and monitor the log file continuously
* Whenever total traffic for the past 2 minutes exceeds a certain number on average, print or display a message saying that “High traffic generated an alert - hits = {value}, triggered at {time}”. The default threshold should be 10 requests per second, and should be overridable
* Whenever the total traffic drops again below that value on average for the past 2 minutes, print or display another message detailing when the alert recovered
* Write a test for the alerting logic
* Explain how you’d improve on this application design



# Usage
```
usage: http-log-monitoring.py [-h] [-f [http log files]] [-s stats]
                              [-t threshold] [-a alarm]

HTTP log monitoring console program

optional arguments:
  -h, --help            show this help message and exit
  -f [http log files], --filename [http log files]
                        http log file (default: /tmp/access.log)
  -s stats, --stats stats
                        statistics interval in second (default: 10)
  -t threshold, --threshold threshold
                        threshold used by alarms in request/s (default: 10)
  -a alarm, --alarm alarm
                        alarm interval in second (default: 180)
```

## Test it
[![Build status](https://github.com/pli01/http-log-monitoring/workflows/CI/badge.svg)](https://github.com/pli01/http-log-monitoring)

Tested Linux ad OS/X

* To test in docker with python:3 image
```
make docker-build
```

* Or in a shell
```
make test
```
