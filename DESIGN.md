# key points
* sample logs test files in CLF format
* param: logfile and threshold default value and overridable (args)
* read log file continously (like tail)
* line parser http log : with structured data: host, ident, and special on url path call section -> use Counter
* trigger stats : 10s, hits / section + whole traffic summary
* trigger alarm : 120s , if req > threshold(10/s) and not alert,  send_alert, if not alert and req < threshold , send_alert recovered
* testing prog to simulate alerting
* First quick implementation with simple tail loop with 1s sleep interval (bloking io)

data structure to store 10s of traffic information
{
  'section': Counter({'/': 215, '/report': 193, '/api': 192}),
  'authuser': Counter({'jill': 157, 'james': 157, 'mary': 150, 'frank': 136}),
  'status': Counter({'404': 166, '200': 159, '302': 140, '503': 135}),
  'host': Counter({'10.1.1.1': 210, '127.0.0.1': 203, '192.168.1.1': 187}),
  'request_method': Counter({'GET': 221, 'POST': 192, 'PUT': 187}),
  'size': Counter({'size': 2148651}),
}

# Improvements
* clean daemonize
* Add try/catch error cleanly
* logging and formating function
* follow rotating logs
* Use non blocking IO, poll, event modification and stream, Loop based on event modification (select, poll)
* Time series: circular queue per second: 1s -> 10s -> 120s (2mn) to store timestamp, and data to enhanced statistics
* multi thread and queue
  * 1 thread : continuously read access log file and store strutured data in queue
  * 1 thread stats
  * 1 thread alerting average
* Event-Driven Programming (asyncio, event)
