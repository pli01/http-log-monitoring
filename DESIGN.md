# key points
* daemon app
* sample logs test files in CLF format
* param: logfile and threshold default value and overridable (args)
* read text file continously (like tail)
* line parser http log : with structured data: host, ident, and special attention on url path section
* trigger stats : 10s, hits / section + whole traffic
* trigger alarm : 120s , if req > 10/s
* testing prog to simulate alerting
* First quick implementation with simple tail loop with 1s sleep interval (bloking io)

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
