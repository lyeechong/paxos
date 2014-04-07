#!/usr/bin/python

import socket

s = socket.socket()
host = socket.gethostname()
port = 12345

s.connect((host, port))
s.send('hi there')
print s.recv(1024)
s.close
