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
  @consant
  def LEADER_HEARTBEAT_TIME():
    return -12345
  @constant
  def SEND():
    return "SEND_CONSTANT"

CONST = _Const()

