#!/bin/bash
timeout=10
logfile="/logs/host.access.log"

until [ "$timeout" -le 0 -o -f "$logfile" ] ; do 
  echo -n "."
  (( timeout-- ))
  sleep 1
done
export PYTHONUNBUFFERED=1
./http-log-monitoring.py -f $logfile -a 30 2>&1
