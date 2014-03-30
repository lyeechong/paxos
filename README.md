paxos
=====
Plan:

We'll need the basic messaging framework before we even start on actual Paxos.

Idea:

One socket for each server, all using the localhost address. (Since it mentions that we can assume the clients know who the servers are).

Have each client communicate to the server port.

Having a standard serializable Java object we can send as a message would be handy. (Instead of sending Strings.)
