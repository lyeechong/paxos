import multiprocessing as mp
from pipesClass import square, double, prod
 
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
