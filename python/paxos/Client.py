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
    self.leader_index = 0
    self.leader_time = currentTimeMillis()
    self.LC = 0

  def check_leader_and_modify(self):
    if self.leader_time != CONST.LEADER_HEARTBEAT_TIME and currentTimeMillis() - self.leader_time > CONST.LEADER_TIMEOUT: #More than half a second
      self.leader_index = (self.leader_index+1)%len(self.server_out)
      self.leader_time = currentTimeMillis()
      self.server_out[self.leader_index].send((CONST.ASSIGN_LEADER,))
      print "changing leader"
      #possibly tell everyone else?

  def update_leader_alive(self, leader_index):
    if leader_index != self.leader_index:
      print "client", self.index, "got heartbeat from" ,leader_index, "but thinks that", self.leader_index, "is the leader"
    else:
      self.leader_time = currentTimeMillis()
    

  def master_command(self, commands):
    #commands = (command, args..)
    current = commands[0]
    if current == CONST.SEND:
      message = commands[1]
      tag = (self.index, self.LC)
      self.server_out[self.leader_index].send((CONST.SEND, tag, message))
    elif current == CONST.PRINT_CHAT_LOG:
      print "client", self.index, "print chat"
    elif current == CONST.SKIP_SLOTS:
      #send skip slots to master
      pass
    elif current == CONST.ALL_CLEAR:
      #all_clear
      pass
    elif current == CONST.TIME_BOMB_LEADER:
      #time_bomb_leader
      pass
    else:
      print "Not the right command"

  def run(self):
    print "hello from client", self.index
    self.master_out.send(("C", self.index)) #ack the master
    self.server_out[self.leader_index].send((CONST.ASSIGN_LEADER,)) #tell the leader he's the leader
    while True:
      if self.conn.poll():
        message = self.conn.recv()
        if message[0] == CONST.MASTER:
          #(MASTER, ...)
          self.master_command(message[1:])
        elif message[0] == CONST.HEARTBEAT:
          #(CONST.HEARTBEAT, leader_index)
          self.update_leader_alive(message[1])

      self.check_leader_and_modify()

def start_client(client_index, pipe_in, clients_out, servers_out, master_out):
  my_client = Client(client_index, pipe_in, clients_out, servers_out, master_out)
  my_client.run()

