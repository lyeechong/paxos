#! /usr/bin/python
import multiprocessing as mp
import fileinput
import string
import time
import sys
from Client import start_client
from Server import start_server
from Constants import CONST, const_debug

debug_on = const_debug # if this is true, the debug messages are printed. Turn off before submitting

def dprint(*args):
  '''
  Print for the debug statements.
  Prepends "Master: " before all the strings.
  Can be turned off by settings the debug_on flag to False.
  '''
  if debug_on:
    print "MASTER " + " ".join(map(str, args))
    sys.stdout.flush()

dprint("starting Master!")

if __name__ == "__main__":

  nodes, clients, = [], []
  num_nodes, num_clients = 0, 0
  server_in = []
  server_out = []
  client_in = []
  client_out = []
  master_in = None
  master_out = None

  def all_clear():
    server_alive_count = 0
    for p in nodes:
      if p.is_alive():
        server_alive_count += 1
    if server_alive_count > num_nodes/2:
      # we do have a majority, so poll clients!
      dprint("majority detected, wait for the all clear from clients!")
      dprint("sending all clear req to all servers")
      for client in client_out:
        client.send((CONST.MASTER, CONST.ALL_CLEAR_REQ))
      dprint("send all of the all clear reqs.. now waiting for all the all clear replies")
      client_reply = set()
      while True:
        if master_in.poll(0.25):
          message = master_in.recv()
          if message[0] == CONST.CLIENT and message[1] == CONST.ALL_CLEAR_REPLY:
            client_index = message[2]
            client_reply.add(client_index)
            dprint(client_reply, len(client_reply), num_clients)
            if len(client_reply) == num_clients:
              dprint("breaking out")
              break
          else:
            master_out.send(message)
    else:
      # we don't have a majority alive.. just return
      dprint("not a majority of servers alive for all clear, just return")
  
  for raw_line in fileinput.input():
    line = raw_line.split();    
    dprint("executing: " + raw_line)    
    if line[0] == 'start':
      num_nodes = int(line[1])
      num_clients = int(line[2])
      """ start up the right number of nodes and clients, and store the 
          connections to them for sending further commands """
      dprint("num_nodes:" + str(num_nodes) + "num_clients:" + str(num_clients))
      for i in range(num_clients):
        cout, cin = mp.Pipe()
        client_out.append(cout)
        client_in.append(cin)
      for i in range(num_nodes):
        sout, sin = mp.Pipe()
        server_out.append(sout)
        server_in.append(sin)
      master_out, master_in = mp.Pipe()
      for i in range(num_clients):
        p = mp.Process(target = start_client, args = (i, client_in[i], client_out, server_out, master_out,))
        clients.append(p)
        p.start()
      for i in range(num_nodes):
        p = mp.Process( target = start_server, args = (i, server_in[i], client_out, server_out, master_out,))
        nodes.append(p)
        p.start()      
      server_ack = set()
      client_ack = set()
      # Wait for Acks from servers and clients starting
      while True:
        if master_in.poll(0.25):
          message = master_in.recv()
          if message[0] == "S":
            server_ack.add(message[1])
          elif message[0] == "C":
            client_ack.add(message[1])
          else:
            #put it back in the queue
            master_out.send(message)
        if len(server_ack) == num_nodes and len(client_ack) == num_clients:
          break
            
    if line[0] == 'sendMessage':
      client_index = int(line[1])
      assert client_index >= 0 and client_index < num_clients, "Invalid Client Index:"+str(client_index)
      message = string.join(line[2::])
      """ Instruct the client specified by client_index to send the message
          to the proper paxos node """
      dprint("client: " +  str(client_index) +  "sending: "+ message)
      client_out[client_index].send((CONST.MASTER, CONST.SEND, message))

    if line[0] == 'printChatLog':
      client_index = int(line[1])
      assert client_index >= 0 and client_index < num_clients, "Invalid Client Index:"+str(client_index)
      """ Print out the client specified by client_index's chat history
          in the format described on the handout """
      dprint("client: " + str(client_index) + "printChatLog")
      client_out[CONST.DIST_CLIENT_INDEX].send((CONST.MASTER, CONST.PRINT_CHAT_LOG))
      while True:
        if master_in.poll(0.25):
          message = master_in.recv()
          if message[0] == CONST.CLIENT and message[1] == CONST.ACK:
            break
          else: 
            master_out.send(message)
      time.sleep(0.25)

    if line[0] == 'allClear':
      """ Ensure that this blocks until all messages that are going to 
          come to consensus in PAXOS do, and that all clients have heard
          of them """
      dprint("sending all clear req to all clients")
      all_clear()
      time.sleep(0.25)
        
    if line[0] == 'crashServer':
      node_index = int(line[1])
      assert node_index >= 0 and node_index < num_nodes, "Invalid Server Index:"+str(node_index)
      """ Immediately crash the server specified by node_index """
      currentNode = nodes[node_index]
      dprint("crashing Server " + str(node_index))
      if currentNode.is_alive():
        currentNode.terminate()
        #block until it is dead
        while currentNode.is_alive():
          pass
        dprint("we crashed server" + str(node_index))
      else:
        dprint(str(node_index) + "already_dead")
      time.sleep(0.25)
      
    if line[0] == 'restartServer':
      node_index = int(line[1])
      assert node_index >= 0 and node_index < num_nodes, "Invalid Server Index:"+str(node_index)
      """ Restart the server specified by node_index """
      dprint("restarting server" + str(node_index))
      currentNode = nodes[node_index]
      if not currentNode.is_alive():
        p = mp.Process( target = start_server, args = (node_index, server_in[node_index], client_out, server_out, master_out,))
        nodes[node_index] = p
        #clear out the pipe
        while server_in[node_index].poll():
          server_in[node_index].recv()
        server_out[node_index].send((CONST.MASTER, CONST.RESTART))
        #restart the process
        p.start()
        #block until it is alive
        cur_count = 0
        while cur_count !=2:
          if master_in.poll(0.25):
            message = master_in.recv()
            if message[0] == "S":
              cur_count += 1
            elif message[0] == CONST.SERVER and message[1] == CONST.ACK:
              cur_count +=1
            else:
              master_out.send(message)
      else:
        dprint("node " + node_index + "is still alive")
      time.sleep(0.25)
          
    if line[0] == 'skipSlots':
      amount_to_skip = int(line[1])
      """ Instruct the leader to skip slots in the chat message sequence """
      all_clear()
      client_out[CONST.DIST_CLIENT_INDEX].send((CONST.MASTER, CONST.SKIP_SLOTS, amount_to_skip))
      dprint("skipping slots")
      while True:
        if master_in.poll(0.25):
          message = master_in.recv()
          dprint(message)
          if message == (CONST.SERVER, CONST.SKIP_SLOTS, CONST.ACK):
            break
          else:
            master_out.send(message)
      time.sleep(0.25)
      
    if line[0] == 'timeBombLeader':
      num_messages = int(line[1])
      """ Instruct the leader to crash after sending the number of paxos
          related messages specified by num_messages """
      client_out[CONST.DIST_CLIENT_INDEX].send((CONST.MASTER, CONST.TIME_BOMB_LEADER, num_messages))

  ### FINISH CLEANING UP ###
  
  for pipe in server_in:
    pipe.close()
  for pipe in server_out:
    pipe.close()
  for pipe in client_in:
    pipe.close()
  for pipe in client_out:
    pipe.close()
  if master_in:
    master_in.close()
  if master_out:
    master_out.close()
  for p in nodes:
    if p.is_alive():
      p.terminate()
  for p in clients:
    if p.is_alive():
      p.terminate()
  
else:
  dprint("something went horribly wrong")
