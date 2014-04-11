#!/usr/bin/evn python

class Proposer():
  def __init__(self, num_nodes):
    self.num_nodes = num_nodes
    self.ballot_num = 0
    self.promises = set()

  def new_proposal():
    self.promises.clear()
    
  def get_ballot_num(self):
    ret_num = self.ballot_num
    self.ballot_num += 1
    return ret_num
  
  def recv_promise(self, accept_index):
    self.promises.add(accept_index)

  def is_promise_majority(self):
    return len(self.promises) > (self.num_nodes / 2)
