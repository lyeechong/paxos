#!/usr/bin/env python

from Constants import CONST, const_debug
import time
import sys

currentTimeMillis = lambda: int(round(time.time() * 1000))

class Client():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.debug_on = const_debug # whether the print messages we use for debugging are printed. Turn this off when we submit

    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out
    #self.leader = [0, CONST.LEADER_HEARTBEAT_TIME] #(leader_index [initially 0], last heartbeattime)
    self.leader_index = 0
    self.leader_time = currentTimeMillis()
    self.LC = 0 # lamport clock
    self.received_tags = set()
    self.messages_sent = {}
    self.chat_log = {}
    
    self.all_clear_checking = False
    self.all_clear_start_time = 0
  
  def dprint(self, *args):
    '''
    Prepends the client's number before the string to be printed.
    More useful for debugging.
    '''
    if self.debug_on:
      print "CLIENT " + str(self.index) + " ".join(map(str, args))
      sys.stdout.flush()

  def check_leader_and_modify(self):
    dTime = currentTimeMillis() - self.leader_time
    if dTime > CONST.TIMEOUT: #More than half a second
      self.leader_index = (self.leader_index+1)%len(self.server_out)
      self.server_out[self.leader_index].send((CONST.ASSIGN_LEADER,))
      self.resubmit_unfinished_messages()
      self.leader_time = currentTimeMillis()
      self.dprint("changing leader to Server " + str(self.leader_index))
      #for tag, msg in self.messages:
      #  self.server_out[self.leader_index].send((CONST.SEND, tag, msg))
      #possibly tell everyone else?

  def update_leader_alive(self, leader_index):
    if leader_index != self.leader_index:
      #print "client", self.index, "got heartbeat from" ,leader_index, "but thinks that", self.leader_index, "is the leader"
      self.leader_index = leader_index
      self.resubmit_unfinished_messages()
      self.dprint("changing leader to Server " + str(self.leader_index))
      self.leader_time = currentTimeMillis()
    else:
      self.leader_time = currentTimeMillis()

  def resubmit_unfinished_messages(self):
    unsent = set(self.messages_sent.keys()).difference(self.received_tags)
    self.dprint("unsent_messages"+str(unsent))
    for tag in unsent:
      message = self.messages_sent[tag]
      del self.messages_sent[tag]
      self.send_message(message)
    
  def send_message(self, message):
    tag = (self.index, self.LC)
    self.LC += 1
    self.dprint("sending message to leader proposer: " + str(message))
    self.server_out[self.leader_index].send((CONST.SEND, tag, message))
    self.messages_sent[tag] = message

  def print_chat_log(self):
    for slot in sorted(self.chat_log.keys()):
      send_index = self.chat_log[slot][0]
      message = self.chat_log[slot][1]
      if message != CONST.NOOP:
        out = ''+str(slot)+" "+str(send_index)+": "+message
        print out
        sys.stdout.flush()
    self.master_out.send((CONST.CLIENT, CONST.ACK))

  def master_command(self, commands):
    #commands = (command, args..)
    current = commands[0]
    if current == CONST.SEND:
      message = commands[1]
      self.send_message(message)
    elif current == CONST.PRINT_CHAT_LOG:
      self.dprint("print chat command issued")
      self.print_chat_log()
    elif current == CONST.SKIP_SLOTS:
      #send skip slots to master
      num_slots = commands[1]
      #for i in range(num_slots):
      #  self.send_message(CONST.NOOP)
      msg = ((CONST.CLIENT, CONST.SKIP_SLOTS, num_slots))
      self.server_out[self.leader_index].send(msg)
    elif current == CONST.ALL_CLEAR_REQ:
      self.all_clear_checking = True #Start checking to see if all messages are sent
    elif current == CONST.TIME_BOMB_LEADER:
      assert self.index == 0, "timebombing when not the distinguished client"
      num_messages = commands[1]
      self.server_out[self.leader_index].send((CONST.TIME_BOMB_LEADER, num_messages)) #timebomb the leader
    else:
      assert False, "invalid command"
    
  def check_for_all_clear(self):
    '''
    This should be called with each iteration of the while loop.
    Check to see if the time has passed and if it has, send back an ALL_CLEAR_REPLY to Master
    and also set the all_clear_checking flag to False.
    '''
    if self.all_clear_checking == True:
      unsent = set(self.messages_sent.keys()).difference(self.received_tags)
      if len(unsent) == 0: # we have sent all ouf messages
        self.dprint("REPLYING TO ALL_CLEAR")
        self.master_out.send((CONST.CLIENT, CONST.ALL_CLEAR_REPLY, self.index))
        #turn the flag off
        self.all_clear_checking = False

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

      if self.all_clear_checking:
        self.check_for_all_clear()
      self.check_leader_and_modify()

def start_client(client_index, pipe_in, clients_out, servers_out, master_out):
  my_client = Client(client_index, pipe_in, clients_out, servers_out, master_out)
  my_client.run()

