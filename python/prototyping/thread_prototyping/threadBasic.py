#!/usr/bin/python

import thread
import time

def print_time(threadName, delay):
  global test
  test = 0
  count = 0
  while count < 5:
    time.sleep(delay)
    count += 1
    test += 1
    print test
    print "%s: %s" % (threadName, time.ctime(time.time()))
    
try:
  thread.start_new_thread(print_time, ("thread-1", 2))
  thread.start_new_thread(print_time, ("thread-2", 4))
except:
  print "Error: unable to start thread"

while 1:
  pass #so that this thread doesn't die
