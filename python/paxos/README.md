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

###TODO:
- ~~Clean up printlines~~
- ~~Have each proposal also have an associate slot number~~
- Check the program still works after Lyee coding in each proposal also containing a slot number
- Update this readme with the new message formats
- check why Master doesn't exit after the end of a file
- Deal with Nacks/Restarting proposals after people die
- Learned messages
- Timeouts on prepare/accept
- All clear command needs to be done in Master
