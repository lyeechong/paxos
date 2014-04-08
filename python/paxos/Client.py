#!/usr/bin/env python

class Client():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out

  def run(self):
    print "hello from client", self.index
    while True:
      message = self.conn.recv()
      print message
      self.master_out.send(message)

def start_client(client_index, pipe_in, clients_out, servers_out, master_out):
  my_client = Client(client_index, pipe_in, clients_out, servers_out, master_out)
  my_client.run()

