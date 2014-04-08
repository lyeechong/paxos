#!/usr/bin/env python

import socket
import sys

host = ''
port = 8888
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
print s.recv(size)

while 1:
    # read from keyboard
    line = sys.stdin.readline().rstrip()
    print line
    if line == "hello" or len(line) < 1:
      break
    s.send(line)
    data = s.recv(size)
    print data
s.close() 
