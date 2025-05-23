# key points of this version
* sample logs test files in CLF format
* param: logfile and threshold default value and overridable (args)
* read log file continuously (like unix tail) and follow rotating logfile
* First quick implementation with simple tail loop with 1s sleep interval (blocking io)
* line parser http clf log: strict regexp, skip line if not in CLF format
* store entry in structured data (nested dict of counter): host, authuser, status, request_method,  and special url path call section
* data structure to store 10s of traffic information as counters
{
  'section': Counter({'/': 215, '/report': 193, '/api': 192}),
  'authuser': Counter({'jill': 157, 'james': 157, 'mary': 150, 'frank': 136}),
  'status': Counter({'404': 166, '200': 159, '302': 140, '503': 135}),
  'host': Counter({'10.1.1.1': 210, '127.0.0.1': 203, '192.168.1.1': 187}),
  'request_method': Counter({'GET': 221, 'POST': 192, 'PUT': 187}),
  'size': Counter({'size': 21486}),
}
* use current time to trigger and display stats : default 10s, hits / section + whole traffic summary
* trigger and display alarm : default 120s , if req > threshold(10/s) and not alert,  send_alert, if not alert and req < threshold , send_alert recovered
* testing prog to simulate alerting


# Improvements
* clean daemonize
* use config file, or env parameters
* catch regex error if logfile in not in CLF format
* use timestamp from log
* logging and formatting function or sending status into a remote collector in a json format
* Use non blocking IO, poll, event modification and stream, Loop based on event modification (select, poll)
* Time series: circular queue per second: 1s -> 10s -> 120s (2mn) to store timestamp, and data to enhanced statistics
* multi thread and queue
  * 1 thread : continuously read access log file and store structured data in queue
  * 1 thread stats
  * 1 thread alerting average
* Event-Driven Programming (asyncio, event)
* add pytest
