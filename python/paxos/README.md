###COMMANDS
#####MASTER TO CLIENT:

sendMessage - `(MASTER, SEND, msg)`

allClear - `(MASTER, ALL_CLEAR)`

timeBombLeader - `(MASTER, TIME_BOMB_LEADER, numMsgs)`

skipSlots - `(MASTER, SKIP_SLOTS)`

printChatLog - `(MASTER, PRINT_CHAT_LOG)`

#####CLIENT TO SERVER:
sendMessage - `(SEND, tag = <client_index, client_LC> , msg)`

###RUNNING THE THING
`python Master.py < selfTest.test`

###How allClear works as of right now
1) Master sends allClearRequest to all Clients

2) Clients reply with allClearReply if there are no messages in the middle of being paxos'ed

3) If there are messages being paxos'ed, the Client waits for TIMEOUT amount of time hoping the messages finish

4) If TIMEOUT time is reached, the Client sends an allClearReply message back to Master, along with a count of the number of messages which were still being paxos'ed

5) Master waits for all the allClearReplies from the Clients and tallies the number of messages being paxos'ed

6) If there are a non-zero amount of messages being paxos'ed, the Master then checks if a majority of servers are still alive, if so, it waits TIMEOUT amount of time before returning. Otherwise the Master just returns immediately

###TODO:
- ~~Clean up printlines~~
- ~~Have each proposal also have an associate slot number~~
- ~~implement timebombs~~
- ~~check why Master doesn't exit after the end of a file~~
- ~~Deal with Nacks/Restarting proposals after people die~~
- ~~learned messages~~
- ~~timeouts on prepare/accept~~
- ~~all clear command needs to be done in Master~~
- ~~cleaning up printChatLog~~
- ~~blocking when printing the chatlog~~
- testing
