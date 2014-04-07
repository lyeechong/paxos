#!/usr/bin/python

import thread
import threading
import time

def tr(threadName, delay)
  count = 0
  while count < 5:
    time.sleep(delay)
    count += 1
    print "%s: %s" % (threadName, time.ctime(time.time()))
    
try:
  thread.start_new_thread(tr, ("thread-1", 2))
  thread.start_new_thread(tr, ("thread-2", 3))
  
except:
  print "exception"

while 1:
  pass
  

class StoppableThread(threading.Thread):
  """Thread class with a stop() method. The thread itself has to check
  regularly for the stopped() condition."""

  def __init__(self):
      super(StoppableThread, self).__init__()
      self._stop = threading.Event()

  def stop(self):
      self._stop.set()

  def stopped(self):
      return self._stop.isSet()
