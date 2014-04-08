#!/usr/bin/env python

class Server():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out

  def run():
    print "hello"

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = new Client(client_index, pipe_in, clienst_out, servers_out, master)
  my_server.run()

