#! /usr/bin/python
import multiprocessing as mp
import fileinput
import string
from Client import start_client

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
              client_out[i].send("Sup"+str(i))
              try:
                print master_in.recv()
              except EOFError:
                print "nothing happened"
              
        if line[0] == 'sendMessage':
            client_index = int(line[1])
            message = string.join(line[2::])
            """ Instruct the client specified by client_index to send the message
                to the proper paxos node """
        if line[0] == 'printChatLog':
            client_index = int(line[1])
            """ Print out the client specified by client_index's chat history
                in the format described on the handout """
        if line[0] == 'allClear':
            """ Ensure that this blocks until all messages that are going to 
                come to consensus in PAXOS do, and that all clients have heard
                of them """
        if line[0] == 'crashServer':
            node_index = int(line[1])
            """ Immediately crash the server specified by node_index """
        if line[0] == 'restartServer':
            node_index = int(line[1])
            """ Restart the server specified by node_index """
        if line[0] == 'skipSlots':
            amount_to_skip = int(line[1])
            """ Instruct the leader to skip slots in the chat message sequence """
        if line[0] == 'timeBombLeader':
            num_messages = int(line[1])
            """ Instruct the leader to crash after sending the number of paxos
                related messages specified by num_messages """

