#!/usr/bin/env python

def square(pipe1, pipe2):
    close, in_conn = pipe1
    close.close()
    out_conn, _ = pipe2
    try:
        while True:
            x = in_conn.recv()
            out_conn.send(x * x)
    except EOFError:
        out_conn.close()

def prod(pipe):
    out_conn, _ = pipe
    for x in xrange(10):
        out_conn.send(x)
 
    out_conn.close()
 
 
 
def double(unused_pipes, in_pipe, out_pipe):
    for pipe in unused_pipes:
        close, _ = pipe
        close.close()
 
    closep, in_conn = in_pipe
    closep.close()
 
    out_conn, _ = out_pipe
    try:
        while True:
            x = in_conn.recv()
            out_conn.send(x * 2)
    except EOFError:
        out_conn.close()
 
