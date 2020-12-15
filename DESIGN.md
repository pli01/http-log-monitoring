# key points
* daemon app
* sample logs test files in CLF format
* line parser http log : with structured data: host, ident, and special attention on url path section
* param: logfile and threshold default value and overridable (args)
* read file continously (tail)
* trigger stats : 10s, hits / section + whole traffic
* trigger alarm : 120s , if req > 10/s
* testing prog to simulate alerting

# Improvements
* clean catch error
* non blocking IO, poll and stream
* Time series: circular queue per second: 1s -> 10s -> 120s (2mn)
* multi thread and queue
  * 1 thread : continuously read access log file and store strutured data in queue
  * 1 thread stats
  * 1 thread alerting average
* Event-Driven Programming (asyncio, event)
