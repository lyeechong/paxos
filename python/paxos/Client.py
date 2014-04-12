#!/usr/bin/env python

from Constants import CONST
import time
import sys

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
    self.LC = 0 # lamport clock
    self.debug_on = False # whether the print messages we use for debugging are printed. Turn this off when we submit
    self.received_tags = set()
    self.messages_sent = {}
    self.chat_log = {}
  
  def dprint(self, string):
    '''
    Prepends the client's number before the string to be printed.
    More useful for debugging.
    '''
    if self.debug_on:
      print "Client " + str(self.index) + ": " + str(string)

  def check_leader_and_modify(self):
    dTime = currentTimeMillis() - self.leader_time
    if dTime > CONST.TIMEOUT: #More than half a second
      self.leader_index = (self.leader_index+1)%len(self.server_out)
      self.server_out[self.leader_index].send((CONST.ASSIGN_LEADER,))
      self.leader_time = currentTimeMillis()
      self.dprint("changing leader to Server " + str(self.leader_index))
      #for tag, msg in self.messages:
      #  self.server_out[self.leader_index].send((CONST.SEND, tag, msg))
      #possibly tell everyone else?

  def update_leader_alive(self, leader_index):
    if leader_index != self.leader_index:
      #print "client", self.index, "got heartbeat from" ,leader_index, "but thinks that", self.leader_index, "is the leader"
      self.leader_index = leader_index
      self.dprint("changing leader to Server " + str(self.leader_index))
      self.leader_time = currentTimeMillis()
    else:
      self.leader_time = currentTimeMillis()
    
  def send_message(self, message):
    tag = (self.index, self.LC)
    self.LC += 1
    self.server_out[self.leader_index].send((CONST.SEND, tag, message))
    self.messages_sent[tag] = message

  def print_chat_log(self):
    for slot in sorted(self.chat_log.keys()):
      send_index = self.chat_log[slot][0]
      message = self.chat_log[slot][1]
      if message != CONST.NOOP:
        out = ''+str(slot)+" "+str(send_index)+": "+message
        #sys.stdout.write(out)
        print out

  def master_command(self, commands):
    #commands = (command, args..)
    current = commands[0]
    self.dprint("hello"+current)
    if current == CONST.SEND:
      message = commands[1]
      self.send_message(message)
    elif current == CONST.PRINT_CHAT_LOG:
      self.dprint("print chat command issued")
      self.print_chat_log()
    elif current == CONST.SKIP_SLOTS:
      #send skip slots to master
      num_slots = commands[1]
      for i in range(num_slots):
        self.send_message(CONST.NOOP)
    elif current == CONST.ALL_CLEAR:
      #all_clear
      pass
    elif current == CONST.TIME_BOMB_LEADER:
      #time_bomb_leader
      pass
    else:
      self.dprint ("unhandled command " + current)

  def run(self):
    self.dprint( "hello from Client " + str(self.index))
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
        elif message[0] == CONST.DECIDED_SET:
          (tag, slot_num, prop) = message[1]
          self.dprint(str(tag)+str(prop))
          self.received_tags.add(tag)
          self.chat_log[slot_num] = prop

      self.check_leader_and_modify()

def start_client(client_index, pipe_in, clients_out, servers_out, master_out):
  my_client = Client(client_index, pipe_in, clients_out, servers_out, master_out)
  my_client.run()

