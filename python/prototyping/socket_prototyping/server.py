#!/usr/bin/python

import socket

s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))

s.listen(5)
while True:
  c, addr = s.accept()
  print 'Got connection from', addr
  buf = c.recv(64)
  if len(buf) > 0:
    print buf
  c.send('Thank you for connecting')
  c.close()
