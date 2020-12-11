# key points
* daemon app
* sample logs test files in CLF
* param: logfile and threshold default value and overridable (args)
* read file continously (tail)
* line parser http log : with structured data: host, ident, and special attention on url path section
* trigger stats : 10s, hits / section + whole traffic
* trigger alarm : 120s , if req > 10/s
* testing prog to simulate alerting

# Improvements
* clean catch error
* queue
     circular queue per second: 1s -> 10s -> 120s (2mn)
* Event-Driven Programming (asyncio, event)
* multi thread and queue
  * 1 thread : continuously read access log file and store strutured data (dict)
  * 1 thread every 10s :  display formated stats , sections = first part of url path
  * 1 thread alerting average:  past 2mn  if thres > 10rq/s , display message high traffic, if threshold < 10 after 2m, display message
  * store
