from actor import Actor, Channel
from tcp_server import Server
from util import *
from urlparse import urlparse

class TCPDispatcher(Actor):

    def __init__(self,addr):
        #Actor.__init__(self)
        ip, port = addr
        self.name = ip + ':' + str(port)
        self.conn = Server(ip, port, self)
        self.addr = addr
        #self.host = host
        self.running = True
        self.channel = Channel()
        self.callback = {}
        self.tell = ['stop']
        self.ask=[]
        self.url = self.name

    def receive(self,msg):
        #if msg[MODE]==SYNC and msg[TYPE]==CALL:
        #    self.callback[msg[RPC_ID]]= msg[SRC]
        if msg[METHOD]=='stop':
                self.running = False
                self.conn.close()
        else:
            try:
                data = [self.addr,msg]
                self.conn.send(data)
            except Exception,e:
                print e,'TCP ERROR 2'

    def is_local(self, name):
        return name == self.name

    def on_message(self, data):
        print data
        try:
            msg = data[1]
            print msg
            aref = msg[TO]
            aurl = urlparse(aref)
            actors[aurl.path].channel.send(msg)
        except Exception,e:
            print e,'TCP ERROR 1'



#self.host.objects[aurl.path].channel.send(msg)
"""
    if msg[TYPE]==RESULT:
        if pending.has_key(msg[RPC_ID]):
            del pending[msg[RPC_ID]]
            target = self.callback[msg[RPC_ID]]
            del self.callback[msg[RPC_ID]]
            target.send(msg)
    else:
        if msg[MODE]== SYNC:
            msg[TARGET]=msg[SRC]
            msg[SRC]= self.channel
            pending[msg[RPC_ID]] = 1
        aref = msg[TO]
        aurl = urlparse(aref)
        self.host.objects[aurl.path].channel.send(msg)
        """
