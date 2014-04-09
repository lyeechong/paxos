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

    self.LC = 0
    self.is_paxosing = False
    self.messageQueue = Queue.Queue()

  def broadcast_clients(self, message):
    for c_out in self.client_out:
      c_out.send(message)

  def broadcast_servers(self, message):
    for i in len(self.server_out):
      if i != self.index:
        self.server_out[i].send(message)

  def queueMessage(self, tag, message):
    #tag = (client_index, client_LC)
    tagged_message = (tag, message)
    self.messageQueue.put(tagged_message)

  def run(self):
    print "hello from server", self.index
    while True:
      if self.conn.poll():
        message = self.conn.recv()
        if message[0] == CONST.ASSIGN_LEADER:
          self.is_leader = True
        if message[0] == CONST.SEND:
          #(CONST.SEND, tag, message)
          self.queueMessage(message[1], message[2])

      if self.is_leader:
        self.broadcast_clients((CONST.HEARTBEAT, self.index))
      
      if not self.is_paxosing and not self.messageQueue.empty():
        message_to_propose = self.messageQueue.get()
        print message_to_propose

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = Server(client_index, pipe_in, clients_out, servers_out, master)
  my_server.run()

