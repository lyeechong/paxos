#!/usr/bin/env python

class Server():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out

  def run(self):
    print "hello from server", self.index

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = Server(client_index, pipe_in, clients_out, servers_out, master)
  my_server.run()

