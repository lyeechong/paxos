import multiprocessing as mp
 
 
def prod(pipe):
    out_conn, _ = pipe
    for x in xrange(10):
        out_conn.send(x)
 
    out_conn.close()
 
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
 
 
def test_pipes():
    pipe1 = mp.Pipe(True)
    p1 = mp.Process(target=prod, args=(pipe1,))
    p1.start()
 
    pipe2 = mp.Pipe(True)
    p2 = mp.Process(target=square, args=(pipe1, pipe2,))
    p2.start()
 
    pipe1[0].close()
    pipe2[0].close()
    
    while True:
      try:
        print pipe2[1].recv()
      except EOFError:
        continue
    print "finished"

"""    try:
        while true:
            print pipe1[1].recv()
            print pipe3[1].recv()
    except EOFError:
        print "Finished"
"""
test_pipes()
