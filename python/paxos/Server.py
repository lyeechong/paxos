#!/usr/bin/env python

from Constants import CONST

class Server():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out
    self.is_leader = False

  def broadcast_clients(self, message):
    for c_out in self.client_out:
      c_out.send(message)

  def run(self):
    print "hello from server", self.index
    while True:
      if self.conn.poll():
        message = self.conn.recv()
        if message[0] == CONST.ASSIGN_LEADER:
          self.is_leader = True

      if self.is_leader:
        self.broadcast_clients((CONST.HEARTBEAT, self.index))

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = Server(client_index, pipe_in, clients_out, servers_out, master)
  my_server.run()

