#!/usr/bin/env python

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

  ### CLIENT CONSTANTS ###
  @constant
  def LEADER_HEARTBEAT_TIME():
    return -12345
  def LEADER_TIMEOUT():
    return 250 #milliseconds

  ### MASTER TO CLIENT ###
  @constant
  def ALL_CLEAR():
    return "ALL_CLEAR_CONSTANT"
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

  ### SERVER TO CLIENT ###
  @constant
  def HEARTBEAT():
    return "HEARTBEAT_CONSTANT"

  ### SERVER TO SERVER ###
  def PROPOSE():
    return "PROPOSE_CONSTANT"

CONST = _Const()

