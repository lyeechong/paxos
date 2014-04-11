#! /usr/bin/python
import multiprocessing as mp
import fileinput
import string
from Client import start_client
from Server import start_server
from Constants import CONST

if __name__ == "__main__":
    nodes, clients, = [], []
    num_nodes, num_clients = 0, 0
    server_in = []
    server_out = []
    client_in = []
    client_out = []
    master_in = None
    master_out = None
    
    for line in fileinput.input():
        line = line.split();
        if line[0] == 'start':
            num_nodes = int(line[1])
            num_clients = int(line[2])
            """ start up the right number of nodes and clients, and store the 
                connections to them for sending further commands """
            print "num_nodes:", num_nodes, "num_clients:", num_clients
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
              if master_in.poll():
                message = master_in.recv()
                if message[0] == "S":
                  server_ack.add(message[1])
                elif message[0] == "C":
                  client_ack.add(message[1])
              if len(server_ack) == num_nodes and len(client_ack) == num_clients:
                break

              
        if line[0] == 'sendMessage':
            client_index = int(line[1])
            message = string.join(line[2::])
            """ Instruct the client specified by client_index to send the message
                to the proper paxos node """
            print "client:", client_index, "sending:", message
            client_out[client_index].send((CONST.MASTER, CONST.SEND, message))

        if line[0] == 'printChatLog':
            client_index = int(line[1])
            """ Print out the client specified by client_index's chat history
                in the format described on the handout """
            print "client:", client_index, "printChatLog"

        if line[0] == 'allClear':
            """ Ensure that this blocks until all messages that are going to 
                come to consensus in PAXOS do, and that all clients have heard
                of them """
            print "allClear"
            clients_out[CONST.DIST_CLIENT_INDEX].send((CONST.MASTER, CONST.ALL_CLEAR))
        if line[0] == 'crashServer':
            node_index = int(line[1])
            """ Immediately crash the server specified by node_index """
            print "crashing server", node_index
            currentNode = nodes[node_index]
            if currentNode.is_alive():
              currentNode.terminate()
            #block until it is dead
            while currentNode.is_alive():
              continue
        if line[0] == 'restartServer':
            node_index = int(line[1])
            """ Restart the server specified by node_index """
            print "restarting server", node_index
            currentNode = nodes[node_index]
            if not currentNode.is_alive():
              p = mp.Process( target = start_server, args = (node_index, server_in[node_index], client_out, server_out, master_out,))
              nodes[node_index] = p

              #clear out the pipe
              while server_in[node_index].poll():
                server_in[node_index].recv()
              server_out[node_index].send(CONST.MASTER, CONST.RESTART)
              p.start()
              #block until it is alive
              while not currentNode.is_alive():
                continue
            else:
              print "node ", node_index, "is still alive"
              
        if line[0] == 'skipSlots':
            amount_to_skip = int(line[1])
            """ Instruct the leader to skip slots in the chat message sequence """
            print "skipSlots", amount_to_skip
            clients_out[CONST.DIST_CLIENT_INDEX].send((CONST.MASTER, CONST.SKIP_SLOTS))
        if line[0] == 'timeBombLeader':
            num_messages = int(line[1])
            """ Instruct the leader to crash after sending the number of paxos
                related messages specified by num_messages """
            print 'timeBombLeader', num_messages
            clients_out[CONST.DIST_CLIENT_INDEX].send((CONST.MASTER, CONST.TIME_BOMB_LEADER))
  
