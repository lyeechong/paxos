#!usr/bin/env python

def dprint(*args):
  print "MASTER"+" ".join(map(str, args))

dprint("hello", "world")
