#!/usr/bin/env python

from Constants import CONST
import Queue
import time

currentTimeMillis = lambda: int(round(time.time() * 1000))

class Server():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out
    self.is_leader = False
    self.num_nodes = len(servers_out)

    self.is_paxosing = False # if there is a proposal
    self.messageQueue = []

    self.ballot_num = 0
    self.proposals = {}
    self.prep_accept = set()
    self.prep_response = set()

    self.current_max_ballot = (-1, -1) # (server number, ballot number)
    self.learned_messages = {}
    self.isLearning = False

    self.server_alive = {}
    
    self.debug_on = True # whether the print messages we use for debugging are printed. Turn this off when we submit
    
    currentTime = currentTimeMillis()
    
    for i in range(self.num_nodes):
      self.server_alive[i] = currentTime
    self.learned_from = set()
    
    self.decided = {}
    
  def dprint(self, string):
    '''
    Prepends the server's number before the string to be printed.
    More useful for debugging.
    '''
    if self.debug_on:
      print "Server " + str(self.index) + ": " + str(string)

  # we can use this to take care of time bombs
  def send_server(self, server_index, message):
    self.server_out[server_index].send(message)

  def broadcast_clients(self, message):
    for c_out in self.client_out:
      c_out.send(message)

  def broadcast_servers(self, message):
    for i in range(len(self.server_out)):
      self.send_server(i, message)

  def queueMessage(self, tag, message):
    #tag = (client_index, client_LC)
    tagged_message = (tag, message)
    self.messageQueue.append(tagged_message)

  def update_servers_heartbeat(self, server_index):
    self.server_alive[server_index] = currentTimeMillis()
  
  def update_servers_alive(self):
    current_time = currentTimeMillis()
    for server_index, last_time in self.server_alive.items():
      if current_time - last_time > CONST.TIMEOUT:
        del self.server_alive[server_index]
        self.dprint(server_index + "dead")

  def start_paxos(self, tagged_message):
    _client_tag = tagged_message[0]
    msg = tagged_message[1]
    self.dprint(str(_client_tag) + str(msg) + "hi" + str(self.is_paxosing))
    ballot = self.get_ballot_num()
    server_tag = (self.index, ballot)
    self.proposals[server_tag] =  {CONST.CLIENT_TAG: _client_tag,
                                    CONST.MESSAGE: msg,
                                    CONST.PREP_MAJORITY: False,
                                    CONST.PREP_ACCEPT: set(),
                                    CONST.PREP_NACK: set(),
                                    CONST.ACCEPT_MAJORITY: False,
                                    CONST.ACCEPT_ACK: set(),
                                    CONST.ACCEPT_NACK: set()}
    #PREPARE()
    self.broadcast_servers((CONST.PROPOSER, CONST.PREPARE, server_tag))
  
  def get_ballot_num(self):
    ret_num = self.ballot_num
    self.ballot_num += 1
    return ret_num

  def compare_ballot(self, server_tag):
    (server_index, ballot) = server_tag
    (c_index, c_ballot) = self.current_max_ballot
    if ballot > c_ballot:
      return True
    if server_index < c_index:
      return False
    return True
  

  def from_proposer(self, args):
    command = args[0]
    self.dprint("from proposer: " + str(args))
    if command == CONST.PREPARE:
      server_tag = args[1]
      (server_index, ballot) = server_tag
      msg = ()
      if self.compare_ballot(server_tag):
        self.current_max_ballot = server_tag
        msg = (CONST.ACCEPTOR, CONST.PREPARE, CONST.ACK, self.index, server_tag)
      else:
        msg = (CONST.ACCEPTOR, CONST.PREPARE, CONST.NACK, self.index, server_tag)
      self.send_server(server_index, msg)
    elif command == CONST.ACCEPT:
      self.dprint("proposer gave command accept with args: " + str(args))
      server_tag = args[1]
      (server_index, ballot) = server_tag
      msg = ()
      if self.compare_ballot(server_tag):
        msg = (CONST.ACCEPTOR, CONST.ACCEPT, CONST.ACK, self.index, server_tag)
      else:
        msg = (CONST.ACCEPTOR, CONST.ACCEPT, CONST.NACK, self.index, server_tag)
      self.send_server(server_index, msg)
    elif command == CONST.DECIDE:
      self.dprint("proposer gave command decide")
      server_tag = args[1]
      message = args[2]
      client_index = args[3]
      slot_num = args[4]
      self.decided[slot_num] = (client_index, message)
      if self.is_leader:
        self.dprint("I am the leader and I'm going to send")
        msg = (CONST.DECIDED_SET, self.decided)
        self.broadcast_clients(msg)

  def from_acceptor(self, args):
    self.dprint("from acceptor: " + str(args))
    command = args[0]
    if command == CONST.PREPARE:
      response = args[1]
      accept_index = args[2]
      server_tag = args[3]
      this_proposal = self.proposals[server_tag]
      if response == CONST.ACK:
        this_proposal[CONST.PREP_ACCEPT].add(accept_index)
        if len(this_proposal[CONST.PREP_ACCEPT]) > self.num_nodes/2 and not this_proposal[CONST.PREP_MAJORITY]:
          self.dprint("got all the promises for" + str(this_proposal[CONST.MESSAGE]))
          this_proposal[CONST.PREP_MAJORITY] = True
          msg = (CONST.PROPOSER, CONST.ACCEPT, server_tag, this_proposal[CONST.MESSAGE])
          self.broadcast_servers(msg)
      elif response == CONST.NACK:
        #TODO
        #any nacks should abort and prepend the proposal to the beginning of message queue
        self.dprint("abort! got nack")
    elif command == CONST.ACCEPT:
      response = args[1]
      accept_index = args[2]
      server_tag = args[3]
      this_proposal = self.proposals[server_tag]
      if response == CONST.ACK:
        this_proposal[CONST.ACCEPT_ACK].add(accept_index)
      if len(this_proposal[CONST.ACCEPT_ACK]) > self.num_nodes/2 and not this_proposal[CONST.ACCEPT_MAJORITY]:
        self.dprint("got all the accepts for" + str(this_proposal[CONST.MESSAGE]))       
        this_proposal[CONST.ACCEPT_MAJORITY] = True
        # PROPOSER, DECIDE, SERVER_TAG, MESSAGE, CLIENT_INDEX, SLOT_NUM
        msg = (CONST.PROPOSER, CONST.DECIDE, server_tag, this_proposal[CONST.MESSAGE], this_proposal[CONST.CLIENT_TAG][0], 0)
        self.broadcast_servers(msg)
      elif response == CONST.NACK:
        #TODO
        #any nacks should abort and prepend the proposal to the begining of message queue
        self.dprint("abort! got nack")

  def run(self):
    self.dprint("hello! server is now running!")
    self.master_out.send(("S", self.index)) # ack the master
    while True:
      if self.is_leader:
        self.broadcast_clients((CONST.HEARTBEAT, self.index))
      #for i in range(self.num_nodes):
      #  if i != self.index:
      #    self.server_out[i].send((CONST.HEARTBEAT, self.index))

      if self.conn.poll():
        message = self.conn.recv()
        self.dprint("got a message!: " + str(message))
        if message[0] == CONST.ASSIGN_LEADER:
          self.is_leader = True
          self.dprint("I am the leader!")
        elif message[0] == CONST.HEARTBEAT:
          self.update_servers_heartbeat(message[1])
        elif message[0] == CONST.SEND:
          #(CONST.SEND, tag, message)
          self.queueMessage(message[1], message[2])

        elif message[0] == CONST.PROPOSER:
          self.from_proposer(message[1:])
        elif message[0] == CONST.ACCEPTOR:
          self.from_acceptor(message[1:])

      
      if not self.is_paxosing and len(self.messageQueue)>0:
        message_to_propose = self.messageQueue.pop(0)
        self.is_paxosing = True
        self.start_paxos(message_to_propose)

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = Server(client_index, pipe_in, clients_out, servers_out, master)
  my_server.run()

