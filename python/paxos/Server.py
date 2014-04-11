#!/usr/bin/env python

from Constants import CONST
import Queue

class Server():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out
    self.is_leader = False
    self.num_nodes = len(servers_out)

    self.is_paxosing = False
    self.messageQueue = Queue.Queue()

    self.ballot_num = 0
    self.proposals = {}
    self.prep_accept = set()
    self.prep_response = set()

    self.current_max_ballot = -1
    self.learned_messages = {}

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
    self.messageQueue.put(tagged_message)

  def start_paxos(self, tagged_message):
    _client_tag = tagged_message[0]
    msg = tagged_message[1]
    print _client_tag, msg, "hi", self.is_paxosing
    ballot = self.get_ballot_num()
    server_tag = (self.index, ballot)
    self.proposals[server_tag] =  {CONST.CLIENT_TAG: _client_tag,
                                    CONST.MESSAGE: msg,
                                    CONST.PREP_ACCEPT: set(),
                                    CONST.PREP_RESPONSE: set()}
    #PREPARE()
    self.broadcast_servers((CONST.PROPOSER, CONST.PREPARE, server_tag))
  
  def get_ballot_num(self):
    ret_num = self.ballot_num
    self.ballot_num += 1
    return ret_num

  def from_proposer(self, args):
    command = args[0]
    print args
    if command == CONST.PREPARE:
      server_tag = args[1]
      (server_index, ballot) = server_tag
      msg = ()
      if ballot > self.current_max_ballot:
        self.current_max_ballot = ballot
        msg = (CONST.ACCEPTOR, CONST.PREPARE, CONST.ACK, self.index, server_tag)
      else:
        msg = (CONST.ACCEPTOR, CONST.PREPARE, CONST.NACK, self.index, server_tag)
      self.send_server(server_index, msg)

  def from_acceptor(self, args):
    print "from"
    command = args[0]
    if command == CONST.PREPARE:
      response = args[1]
      accept_index = args[2]
      server_tag = args[3]
      self.proposals[server_tag][CONST.PREP_RESPONSE].add(accept_index)
      if response == CONST.ACK:
        self.proposals[server_tag][CONST.PREP_ACCEPT].add(accept_index)
      if len(self.proposals[server_tag][CONST.PREP_ACCEPT]) > self.num_nodes/2:
        print "yay we got all the promises!"

  def run(self):
    print "hello from server", self.index
    self.master_out.send(("S", self.index)) # ack the master
    while True:
      if self.conn.poll():
        message = self.conn.recv()
        if message[0] == CONST.ASSIGN_LEADER:
          self.is_leader = True
        elif message[0] == CONST.SEND:
          #(CONST.SEND, tag, message)
          self.queueMessage(message[1], message[2])

        elif message[0] == CONST.PROPOSER:
          self.from_proposer(message[1:])
        elif message[0] == CONST.ACCEPTOR:
          self.from_acceptor(message[1:])

      if self.is_leader:
        self.broadcast_clients((CONST.HEARTBEAT, self.index))
      
      if not self.is_paxosing and not self.messageQueue.empty():
        message_to_propose = self.messageQueue.get()
        self.is_paxosing = True
        self.start_paxos(message_to_propose)

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = Server(client_index, pipe_in, clients_out, servers_out, master)
  my_server.run()

