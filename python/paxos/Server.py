#!/usr/bin/env python

from Constants import CONST, const_debug
import Queue
import sys
import time

currentTimeMillis = lambda: int(round(time.time() * 1000))

class Server():
  def __init__(self, client_index, pipe_in, clients_out, servers_out, master_out):
    self.debug_on = const_debug # whether the print messages we use for debugging are printed. Turn this off when we submit


    self.index = client_index
    self.conn = pipe_in
    self.client_out = clients_out
    self.server_out = servers_out
    self.master_out = master_out
    self.is_leader = False
    self.num_nodes = len(servers_out)

    self.is_paxosing = False # if there is a proposal
    self.messageQueue = [] # the proposals which are to be sent out

    self.ballot_num = 0 # this server's strictly increasing ballot numbers
    self.proposals = {} # the current set of proposals which originated from this server
    self.prep_accept = set()
    self.prep_response = set()
    
    self.highest_competing_ballot_value = {} # a mapping of slot number to the highest ballot number which has been proposed (we don't need to store the actual proposal message)

    self.learned_messages = {} # is this used??
    self.isLearning = False # huh??

    self.server_alive = {}
    
    self.current_spot_request = None # the current spot request
    self.current_proposal_waiting_for_acks = False # whether we're waiting for acks/nacks    
    self.current_proposal_time = -1 # the time we sent out the proposal. Used to check for timeout for nacks/acks
    
    self.timebomb_active = False # whether the timebomb is active
    self.timebomb_counter = -1 # timebomb counter
    
    self.decided = {} # mapping of spot numbers to messages
    
  def dprint(self, *args):
    '''
    Prepends the server's number before the string to be printed.
    More useful for debugging.
    '''
    if self.debug_on:
      print "SERVER "+" ".join(map(str, args))
      sys.stdout.flush()

  # we can use this to take care of time bombs
  def send_server(self, server_index, message):
    self.server_out[server_index].send(message)
    if self.timebomb_active:
      self.check_timebomb()

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
    '''
    starts "paxosing" for a specific message a client wants
    '''
    # tagged message is the message the client is requesting
    _client_tag = tagged_message[0]
    msg = tagged_message[1]
    assert (self.is_paxosing), "we started paxos for a client message but the paxosing flag isn't set!"
    self.dprint("begin paxosing for message " + str(_client_tag) + str(msg))
    ballot_number = self.get_ballot_num() # grab a ballot number to create a new ballot
    proposed_spot = self.get_free_spot()
    self.current_proposal_waiting_for_acks = True
    spot_request = (self.index, ballot_number, proposed_spot) # formerly called server_tag
    self.current_spot_request = spot_request
    self.proposals[spot_request] =  {CONST.CLIENT_TAG: _client_tag,
                                    CONST.MESSAGE: msg,
                                    CONST.PREP_MAJORITY: False,
                                    CONST.PREP_ACCEPT: set(),
                                    CONST.PREP_NACK: set(),
                                    CONST.ACCEPT_MAJORITY: False,
                                    CONST.ACCEPT_ACK: set(),
                                    CONST.ACCEPT_NACK: set()}
    self.current_proposal_time = currentTimeMillis()    
    #PREPARE()
    self.broadcast_servers((CONST.PROPOSER, CONST.PREPARE, spot_request))
  
  def get_free_spot(self):
    '''
    finds the next free spot a message can fit in (based off the current set of decided values) and returns it
    '''
    """
    temp = self.decided.keys()
    temp.sort()
    if not temp:
      # the mapping is empty!
      return 0
    else:
      return temp[-1] + 1 # this is the next free spot since we're skipping the skipped slots    
    """
    return len(self.decided)
  def get_ballot_num(self):
    '''
    returns the next ballot number of this server
    '''
    ret_num = self.ballot_num
    self.ballot_num += 1
    return ret_num

  def update_competing_ballots(self, spot_request):
    '''
    Compares two ballots and returns True if the ballot passed to this method
    has a higher value than the current ballot value for the spot, otherwise returns False.
    If the ballot happened to have a higher value than the previous, also update
    the highest_competiting_ballot_value mapping.
    '''
    (server_index, new_ballot_val, requested_spot) = spot_request
    # check if the requested spot already has a competing ballot value
    if requested_spot in self.highest_competing_ballot_value.keys():
      # there is a competing ballot value, so compare ballot values
      (current_server_index, current_ballot_value) = self.highest_competing_ballot_value[requested_spot]
      if new_ballot_val == current_ballot_value:
        # there's a tie! so check leader numbers
        if server_index >= current_server_index: # >= because it might be the same ballot
          self.highest_competing_ballot_value[requested_spot] = (server_index, new_ballot_val)
          return True
        else:
          return False
      elif new_ballot_val > current_ballot_value:
        self.highest_competing_ballot_value[requested_spot] = (server_index, new_ballot_val)
        return True
      else:
        return False
    else:
      # there is no competiting ballot value, so set this ballot to be the current highest ballot
      self.highest_competing_ballot_value[requested_spot] = (server_index, new_ballot_val)
      return True

  def from_proposer(self, args):
    command = args[0]
    self.dprint("from proposer: " + str(args))
    if command == CONST.PREPARE:
      spot_request = args[1]
      (server_index, ballot_num, requested_spot) = spot_request
      msg = ()
      if self.update_competing_ballots(spot_request):
        msg = (CONST.ACCEPTOR, CONST.PREPARE, CONST.ACK, self.index, spot_request)
      else:
        msg = (CONST.ACCEPTOR, CONST.PREPARE, CONST.NACK, self.index, spot_request)
      self.send_server(server_index, msg)
    elif command == CONST.ACCEPT:
      self.dprint("proposer gave command accept with args: " + str(args))
      spot_request = args[1]
      (server_index, ballot_num, requested_spot) = spot_request
      msg = ()
      if self.update_competing_ballots(spot_request):
        msg = (CONST.ACCEPTOR, CONST.ACCEPT, CONST.ACK, self.index, spot_request)
      else:
        msg = (CONST.ACCEPTOR, CONST.ACCEPT, CONST.NACK, self.index, spot_request)
      self.send_server(server_index, msg)
    elif command == CONST.DECIDE:
      self.dprint("proposer gave command decide")
      spot_request = args[1]
      message = args[2]
      client_index = args[3]
      (server_index, ballot_num, requested_spot) = spot_request
      self.decided[requested_spot] = (client_index, message) # put the message in the requested spot
      if self.is_leader:
        self.dprint("I am the leader and I'm going to send") # huhhhh?
        # (DECIDE, CLIENT_TAG, REQUEST_SPOT, (INDEX, MSG))
        msg = (CONST.DECIDED_SET, (self.proposals[spot_request][CONST.CLIENT_TAG], requested_spot, self.decided[requested_spot]))
        self.broadcast_clients(msg)
        self.is_paxosing = False

  def from_acceptor(self, args):
    self.dprint("from acceptor: " + str(args))
    command = args[0]
    if command == CONST.PREPARE:
      response = args[1]
      accepted_server_number = args[2]
      spot_request = args[3]
      this_proposal = self.proposals[spot_request]
      if response == CONST.ACK:
        this_proposal[CONST.PREP_ACCEPT].add(accepted_server_number)
        if len(this_proposal[CONST.PREP_ACCEPT]) > self.num_nodes/2 and not this_proposal[CONST.PREP_MAJORITY]:
          self.dprint("got all the promises for" + str(this_proposal[CONST.MESSAGE]))
          this_proposal[CONST.PREP_MAJORITY] = True
          msg = (CONST.PROPOSER, CONST.ACCEPT, spot_request, this_proposal[CONST.MESSAGE])
          self.current_proposal_waiting_for_acks = False
          self.broadcast_servers(msg)
      elif response == CONST.NACK:
        #TODO
        #any nacks should abort and prepend the proposal to the beginning of message queue
        self.dprint("abort! got nack")
        self.abort_paxos(spot_request)
    elif command == CONST.ACCEPT:
      response = args[1]
      accept_index = args[2]
      spot_request = args[3]
      this_proposal = self.proposals[spot_request]
      if response == CONST.ACK:
        this_proposal[CONST.ACCEPT_ACK].add(accept_index)
      if len(this_proposal[CONST.ACCEPT_ACK]) > self.num_nodes/2 and not this_proposal[CONST.ACCEPT_MAJORITY]:
        self.current_proposal_waiting_for_acks = False
        self.dprint("got all the accepts for" + str(this_proposal[CONST.MESSAGE]))       
        this_proposal[CONST.ACCEPT_MAJORITY] = True
        # PROPOSER, DECIDE, SPOT_REQUEST, MESSAGE, CLIENT_INDEX
        msg = (CONST.PROPOSER, CONST.DECIDE, spot_request, this_proposal[CONST.MESSAGE], this_proposal[CONST.CLIENT_TAG][0])
        self.broadcast_servers(msg)
      elif response == CONST.NACK:
        #TODO
        #any nacks should abort and prepend the proposal to the begining of message queue
        self.current_proposal_waiting_for_acks = False
        self.dprint("abort! got nack")
        self.abort_paxos(spot_request)
        
  def check_ack_timeout(self):
    '''
    Check if we've been waiting too long for acks/nacks to come back for a proposal
    '''
    if self.is_paxosing and self.current_proposal_waiting_for_acks: # only need to check if we're paxosing and currently waiting for acks
      dTime = currentTimeMillis() - self.current_proposal_time
      if dTime > CONST.TIMEOUT * 4: # I suppose 1 second is long enough
        self.dprint("timed out on the current proposal's acks/nacks!")
        self.current_proposal_waiting_for_acks = False
        self.abort_paxos(self.current_spot_request)

  def abort_paxos(self, spot_request):
    this_proposal = self.proposals[spot_request]
    self.messageQueue.insert(0, (this_proposal[CONST.CLIENT_TAG], this_proposal[CONST.MESSAGE]))
    self.is_paxosing = False
    
  def deal_with_timebomb(self, args):
    '''
    handles a timebomb request, setting the current_timebomb_countdown to the appropriate value
    '''
    requested_countdown = args[0]
    self.dprint("timebomb received with a value of: " + str(requested_countdown))
    assert self.is_leader, "got a timebomb but this server isn't the leader!"
    self.timebomb_active = True
    self.timebomb_counter = requested_countdown # timebomb counter
    self.dprint("timebomb with value of " + str(requested_countdown) + " now is active!")
    assert self.timebomb_active
    assert self.timebomb_counter == requested_countdown
    
  def check_timebomb(self):
    '''
    Should be called everytime we send a non-heartbeat message.
    Checks if a timebomb is active, and if it is, decrement the counter.
    '''
    assert self.is_leader, "this server has a timebomb but isn't the leader"
    self.dprint("timebomb on this server being decremented from " + str(self.timebomb_counter) + " to " + str(self.timebomb_counter-1))
    self.timebomb_counter -= 1
    if self.timebomb_counter <= 0:
      # boom!
      self.dprint("timebomb exploding!")
      sys.exit(0)
      assert false, "SHOULD NOT HAVE REACHED THIS. SERVER SHOULD BE VERY DEAD"

  def run(self):
    self.dprint("hello! This server is now running!")
    self.master_out.send(("S", self.index)) # ack the master
    while True:
      if self.is_leader:
        self.broadcast_clients((CONST.HEARTBEAT, self.index))
        self.check_ack_timeout()
      
      #for i in range(self.num_nodes):
      #  if i != self.index:
      #    self.server_out[i].send((CONST.HEARTBEAT, self.index))

      if self.conn.poll():
        message = self.conn.recv()
        self.dprint("got a message!: " + str(message))
        if message[0] == CONST.ASSIGN_LEADER:
          self.is_leader = True
          self.dprint("I am the leader!")
          assert self.is_leader
        elif message[0] == CONST.HEARTBEAT:
          self.update_servers_heartbeat(message[1])
        elif message[0] == CONST.SEND:
          self.is_leader = True
          #(CONST.SEND, tag, message)
          self.queueMessage(message[1], message[2])
        elif message[0] == CONST.SKIP_SLOTS:
          pass
        elif message[0] == CONST.TIME_BOMB_LEADER:
          self.deal_with_timebomb(message[1:])
        elif message[0] == CONST.PROPOSER:
          self.from_proposer(message[1:])
        elif message[0] == CONST.ACCEPTOR:
          self.from_acceptor(message[1:])

      ''' check to see if there is a waiting proposal from a client in the queue
      and that this server is currently  not in paxos mode. If so, begin paxos on that message '''
      if not self.is_paxosing and len(self.messageQueue) > 0:
        assert self.is_leader, "wanted to start paxosing but this server isn't the leader"
        message_to_propose = self.messageQueue.pop(0)
        self.is_paxosing = True
        self.start_paxos(message_to_propose)

def start_server(client_index, pipe_in, clients_out, servers_out, master):
  my_server = Server(client_index, pipe_in, clients_out, servers_out, master)
  my_server.run()

