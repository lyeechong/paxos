#!/usr/bin/env python
const_debug = False

def constant(f):
  def fset(self, value):
    raise SyntaxError
  def fget(self):
    return f()
  return property(fget, fset)

class _Const(object):

  ### MASTER CONSTANTS ###
  @constant
  def MASTER():
    return "MASTER_CONSTANT"
  @constant
  def DIST_CLIENT_INDEX():
    return 0
  @constant
  def TIMEOUT():
    return 500 #MS
  @constant
  def RESTART():
    return "RESTART_CONSTANT"
  @constant
  def ALL_CLEAR_REQ(): #used to request an allClear
    return "ALL_CLEAR_REQ_CONSTANT"
  @constant
  def ALL_CLEAR_REPLY(): #used to reply to an allClearReq message from Master
    return "ALL_CLEAR_REPLY_CONSTANT"

  ### SERVER CONSTANTS ###
  @constant
  def SERVER():
    return "SERVER_CONSTANT_123"
  @constant
  def PROPOSER():
    return "PROPOSER_CONSTANT_123"
  @constant
  def ACCEPTOR():
    return "ACCEPTOR_CONSTANT_123"
  @constant
  def LEARNER():
    return "LEARNER_CONSTANT_123"
  @constant
  def ACK():
    return "ACK_CONSTANT_123"
  @constant
  def NACK():
    return "NACK_CONSTANT_456"
  @constant
  def REVIVED():
    return "REVIVED_CONSTANT"

  ### PROPOSER CONSTANTS ###
  @constant
  def CLIENT_TAG():
    return "CLIENT_TAG_CONSTANT"
  @constant
  def MESSAGE():
    return "MESSAGE_CONSTANT"
  @constant
  def PREP_MAJORITY():
    return "PREP_MAJORITY_CONSTANT"
  @constant
  def PREP_ACCEPT():
    return "PREP_ACCEPT_CONSTANT"
  @constant
  def PREP_NACK():
    return "PREP_NACK_CONSTANT"
  @constant
  def ACCEPT_ACK():
    return "ACCEPT_ACK_CONSTANT"
  @constant
  def ACCEPT_NACK():
    return "ACCEPT_NACK_CONSTANT"
  @constant
  def ACCEPT_MAJORITY():
    return "ACCEPT_MAJORITY_CONSTANT"
  

  ### CLIENT CONSTANTS ###
  @constant
  def LEADER_HEARTBEAT_TIME():
    return -12345
  @constant
  def LEADER_TIMEOUT():
    return 250 #milliseconds
  @constant
  def CLIENT():
    return "CLIENT_CONSTANT_WOOT_WOOT"

  ### MASTER TO CLIENT ###
  @constant
  def SKIP_SLOTS():
    return "SKIP_SLOTS_CONSTANT"
  @constant
  def TIME_BOMB_LEADER():
    return "TIME_BOMB_LEADER_CONSTANT"
  @constant
  def SEND():
    return "SEND_CONSTANT"
  @constant
  def PRINT_CHAT_LOG():
    return "PRINT_CHAT_LOG_CONSTANT"
  

  ### CLIENT TO SERVER ###
  @constant
  def ASSIGN_LEADER():
    return "ASSIGN_LEADER_CONSTANT"
  @constant
  def NOOP():
    return "NOOP_CONSTANT_WOOT_WOOT"

  ### SERVER TO CLIENT ###
  @constant
  def HEARTBEAT():
    return "HEARTBEAT_CONSTANT"
  @constant
  def DECIDED_SET():
    return "NEW_LEARNED_SET"

  ### SERVER TO SERVER ###
  @constant
  def PREPARE():
    return "PREPARE_CONSTANT"
  @constant
  def PROMISE():
    return "PROMISE_CONSTANT"
  @constant
  def PROPOSE():
    return "PROPOSE_CONSTANT"
  @constant
  def ACCEPT():
    return "ACCEPT_CONSTANT"
  @constant
  def DECIDE():
    return "DECIDE_CONSTANT"


CONST = _Const()

