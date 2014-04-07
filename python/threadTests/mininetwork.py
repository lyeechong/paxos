#!usr/bin/python

import socket
import sys
from thread import *
 
class NodeClass:
  HOST = ''   # Symbolic name meaning all available interfaces
  
  def __init__(self, nodenumber, portnumber, nodelist):
    self.nodenumber = nodenumber
    self.portnumber = portnumber
    run()
    
  def pr(string):
    print self.nodenumber + ": " + string
  
  def run():    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pr('Socket created')
     
    #Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
         
    print 'Socket bind complete'
     
    #Start listening on socket
    s.listen(10)
    print 'Socket now listening'

    counter = 0
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
         
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,))
     
    s.close()
     
  #Function for handling connections. This will be used to create threads
  def clientthread(conn):
      #Sending message to connected client
      conn.send('Welcome to the node ' + self.nodenumber + '.\n') #send only takes string
       
      #infinite loop so that function do not terminate and thread do not end.
      while True:
          #Receiving from client
          data = conn.recv(1024)
          reply = 'OK...' + data
          if not data:
              break
          conn.sendall(reply)
       
      #came out of loop
      conn.close()
      
      
#begin the madness!
portnumber = 50000
for x in range (0, 4):  
  NodeClass(nodenumber, portnumber, nodelist)

