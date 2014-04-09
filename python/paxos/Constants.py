#!/usr/bin/env python

def constant(f):
  def fset(self, value):
    raise SyntaxError
  def fget(self):
    return f()
  return property(fget, fset)

class _Const(object):
  @constant
  def MASTER():
    return "MASTER_CONSTANT"

  ### CLIENT CONSTANTS ###
  @constant
  def HEARTBEAT():
    return "HEARTBEAT_CONSTANT"
  @constant
  def LEADER_HEARTBEAT_TIME():
    return -12345
  @constant
  def SEND():
    return "SEND_CONSTANT"
  @constant
  def PRINT_CHAT_LOG():
    return "PRINT_CHAT_LOG_CONSTANT"
  
  @constant
  def ASSIGN_LEADER():
    return "ASSIGN_LEADER_CONSTANT"

CONST = _Const()

