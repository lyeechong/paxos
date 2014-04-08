#!/usr/bin/env python

from Constants import CONST
import time

currentTimeMillis = lambda: int(round(time.time() * 1000))

class Client():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out
    #self.leader = [0, CONST.LEADER_HEARTBEAT_TIME] #(leader_index [initially 0], last heartbeattime)
    self.leader = [0, 0]

  def check_leader_and_modify(self):
    if self.leader[1] != CONST.LEADER_HEARTBEAT_TIME and currentTimeMillis() - self.leader[1] > 500: #More than half a second
      self.leader[0] = (self.leader[0]+1)%len(self.server_out)
      self.leader[1] = currentTimeMillis()
      print "changing leader"
      #possibly tell everyone else?

  def update_leader_alive(self, leader_index):
    print "updating leader"
    if leader_index != self.leader[0]:
      print "client", self.index, "got heartbeat from" ,leader_index, "but thinks that", self.leader_index[1], "is the leader"
    else:
      self.leader[1] = currentTimeMillis()
    

  def master_command(self, commands):
    if commands[0] == CONST.SEND:
      message = commands[1]
      self.server_out[self.leader[0]].send((CONST.SEND, self.index, message))
    elif commands[0] == CONST.PRINT_CHAT_LOG:
      print "client", self.index, "print chat"

  def run(self):
    print "hello from client", self.index
    while True:
      if self.conn.poll():
        message = self.conn.recv()
        if message[0] == CONST.MASTER:
          self.master_command(message[1:])
        elif message[0] == CONST.HEARTBEAT:
          self.update_leader_alive(message[1])

      self.check_leader_and_modify()

def start_client(client_index, pipe_in, clients_out, servers_out, master_out):
  my_client = Client(client_index, pipe_in, clients_out, servers_out, master_out)
  my_client.run()

