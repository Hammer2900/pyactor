from Queue import Queue,Empty
from threading import Thread
from util import *
from copy import copy


class Channel(Queue):
    """
    Channel is the main communication mechanism between actors. It is actually a
    simple facade to the Queue.Queue python class.
    """
    def __init__(self):
        Queue.__init__(self)

    def send(self,msg):
        """
        It sends a message to the current channel.

        :param msg: The message sent to an actor. It is a tuple using the constants
            in util.py (:mod:`pyactor.util`).
        """
        self.put(msg)

    def receive(self, timeout = None):
        """
        It receives a message from the channel, blocking the calling thread until
        the response is received, or the timeout is triggered.

        :param int timeout: timeout to wait for messages. If none provided it will
            block until a message arrives.
        :return: returns a message sent to the channel. It is a tuple using the
            constants in util.py (:mod:`pyactor.util`).
        """
        return self.get(timeout=timeout)

class ActorRef(object):
    '''
    ActorRef contains the main components of an actor. These are the URL where it
    is located, the communication :class:`~.Channel` and the class of the actor
    as also the synchronous and asynchronous methods the class implements.
    When no channel is specified a new one will be created wich is also the
    default procedure.

    .. note:: This is a superclass of :py:class:`Actor` and has no direct functionality.

    '''
    def __init__(self,url,klass,channel=None):
        self.url = url
        if channel:
            self.channel = channel
        else:
            self.channel = Channel()
        self.tell = copy(klass._tell)
        self.ask = copy(klass._ask)


        if hasattr(klass, '_ref'):
            self.tell_ref = list(set(self.tell) & set(klass._ref))
            self.ask_ref = list(set(self.ask) & set(klass._ref))
            for method in self.ask_ref:
                self.ask.remove(method)
            for method in self.tell_ref:
                self.tell.remove(method)
        else:
            self.ask_ref = []
            self.tell_ref = []

        self.klass = klass

    def __repr__(self):
        return 'Actor(url=%s, class=%s)' % (self.url, self.klass)


class Actor(ActorRef):
    '''
    Actor is the instance of an object to which is possible to acces and invoke
    its methods remotely. Main element of the model. The host is the one to create
    them (spawning -> see :meth:`~.spawn`).

    :param str. url: URL where the actor is running.
    :param class klass: class type for the actor.
    :param klass obj: instance of the *klass* class to attach to the actor.
    '''
    def __init__(self, url, klass, obj):
        super(Actor,self).__init__(url,klass)
        self._obj = obj
        self.id = obj.id
        self.tell.append('stop')
        self.running = True


    def __processQueue(self):
        while self.running:
            message = self.channel.receive()
            self.receive(message)

    def is_alive(self):
        '''
        :return: (*bool.*) identifies the current state of the actor. **True** if
            it is running.
        '''
        return self.running

    def receive(self,msg):
        '''
        The message received from the queue specify a method of the class the
        actor represents. This invokes it. If the communication is an
        :class:`~.AskRequest`, sends the result back to the channel included in
        the message as an :class:`~.AskResponse`.
        If it is a :class:`~.Future`, generates a :class:`~.TellRequest` to send
        the result to the sender's method specified in the callback field of the
        tuple.

        :param msg: The message is a namedtuple of the defined in util.py
            (:class:`~.AskRequest`, :class:`~.TellRequest`, :class:`~.FutureRequest`).
        '''
        if msg.method=='stop':
            self.running = False

        else:
            result = None
            try:
                invoke = getattr(self._obj, msg.method)
                params = msg.params
                result = invoke(*params)

            except Exception, e:
                result = e
                print result
        if msg.type == ASK:
            response = AskResponse(result)
            msg.channel.send(response)
        if msg.type == FUTURE:
            response = TellRequest(TELL,msg.callback,[result],msg.from_url)
            #response = (msg[TO],msg[FROM],TELL, msg[FUTURE],[result])
            #response = TellRequest(TELL,msg.callback,[result],msg.from)
            msg.channel.send(response)


    def run(self):
        '''
        Creates the actor thread wich will process the channel queue while the
        actor :meth:`is_alive`, making it able to receive queries.
        '''
        self.thread = Thread(target=self.__processQueue)
        self.thread.start()
