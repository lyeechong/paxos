import multiprocessing as mp
import time
import sys

def explode_after_time(process_num):
  for i in range (0, 25):
    time.sleep(process_num/10.0)
    if i == process_num:
      print "process ", process_num, " killing itself!"  
      sys.exit(0)
    print "hello #", i, " from process ", process_num
    
processes = []
for i in range(10, 15):
  p = mp.Process(target=explode_after_time, args=(i,))
  processes.append(p)
  p.start()
  
for i in range(0, 5):
  pass
  processes[i].join()
