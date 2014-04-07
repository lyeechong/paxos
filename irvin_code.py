from multiprocessing import Pipe

cp = []
cg = []
sp = []
sg = []

for c in clients:
  post, get = Pipe()
  cp.append(post)
  cg.append(get)
  


c = Client(sp, cg[i])

class Client():
  def __init__(self, servers, myconn):
    self.servers = servers
    self.conn = myconn
    
  def run():
    while True:
      m = self.conn.recv()
      
      # m = ("send", message)
      if m[0] = 'send':
        self.servers[leader_index].send(m)
        
        
class Server():
  def __init__(self, servers, clients, my_index):
    self.conn = servers[my_index]
    self.index = my_index
   
   def propose(self, m):
    for s in servers:
      s.send(("promise", self.index, slot_num, m))
      
    while True:
      m = self.conn.recv()
      
      if m[0] == 'ack':
        
   
   def run():
    while True:
      if self.conn.poll():
        m = self.conn.recv()
      else:
        continue
        
      if m[0] == 'send':
        # I'm the leader!
        self.propose(m)
        
      elif m[0] == 'promise':
        # m[1] must be the leader!
        Check my promise set, if m[2] is valid, acknowledge
        self.servers[m[1]].send(("ack", self.index, slot_num, m))
        
        
        
        
