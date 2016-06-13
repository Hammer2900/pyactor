import signal
import sys
import threading

from urlparse import urlparse
from copy import copy
from time import sleep

from actor import Actor, ActorRef
from parallels import ActorParallel
from pyactor.intervals import interval_host
from proxy import Proxy
from util import *
import util

CLEAN_INT = 4


def create_host(url="local://local:6666/host"):
    '''
    This is the main function to create a new Host to which you can
    spawn actors. It will be set by default at local address if no
    parameter *url* is given. This function shuould be called once for
    execution or after callig :meth:`~.shutdown` to the previous host.
    Only one host can be alive at a time, trying to create more than
    one will raise an exception.

    :param str. url: URL where to start and bind the host.
    :return: :class:`~.Host` created.
    :rise: Exception if there is a host already created.
    '''
    if url in util.hosts.keys():
        raise Exception('Host already created. Only one host can' +
                        ' be ran with the same url.')
    else:
        if not util.hosts:
            util.main_host = Host(url)
            util.hosts[url] = util.main_host
        else:
            util.hosts[url] = Host(url)
        return util.hosts[url]


class Host(object):
    '''
    Host must be created using the function :func:`~create_host`.

    Host is the container of the actors. It manages the spawn and
    elimination of actors and their communication through channels. Also
    configures the TCP socket where the actors will be able to receive
    queries remotely. Additionaly, controls the correct management of
    the threads and intervals of its actors.

    The host can be managed as a simple object, but it also is an actor
    itself so you can get its :class:`~.Proxy` (with ``host.proxy``) and
    pass it to another host to spawn remotely.

    :param str. url: URL that identifies the host.
    '''
    _tell = ['attach_interval', 'detach_interval']
    _ask = ['spawn', 'lookup', 'spawn_n', 'lookup_url']

    def __init__(self, url):
        self.actors = {}
        self.threads = {}
        self.pthreads = {}
        self.intervals = {}
        self.locks = {}
        self.url = url
        self.running = False
        self.alive = True
        self.load_transport(url)
        self.init_host()

        # self.cleaner = interval_host(get_host(), CLEAN_INT, self.do_clean)

    def load_transport(self, url):
        '''
        ### Not yet functional
        For TCP communication. Sets the communication socket of the host
        at the address and port specified.

        :param str. url: URL where to bind the host. Must be provided in
            the tipical form: 'scheme://address:port/hierarchical_path'
        '''
        aurl = urlparse(url)
        addrl = aurl.netloc.split(':')
        self.addr = addrl[0], addrl[1]
        self.transport = aurl.scheme
        self.host_url = aurl

        # if aurl.scheme == 'tcp':
        #     self.tcp = Server(self.addr)
        #     dispatcher = self.tcp.get_dispatcher(self.addr)
        #     launch_actor(self.addr,dispatcher)

    def spawn(self, id, klass, args=[]):
        '''
        This method creates an actor attached to this host. It will be
        an instance of the class *klass* and it will be assigned an ID
        that identifies it among the host.

        This method can be called remotely synchronously.

        :param str. id: identifier for the spawning actor. Unique within
            the host.
        :param class klass: class type of the spawning actor.
        :param list args: arguments for the init function of the
            spawning actor class.
        :return: :class:`~.Proxy` of the actor spawned.
        :raises: :class:`AlreadyExists`, if the ID specified is already
            in use.
        :raises: :class:`HostDown` if there is no host initiated.
        '''
        if not self.alive:
            raise HostDown()
        url = '%s://%s/%s' % (self.transport, self.host_url.netloc, id)
        if url in self.actors.keys():
            raise AlreadyExists()
        else:
            obj = klass(*args)
            obj.id = id
            if self.running:
                obj.host = self.proxy
            # else:
            #     obj.host = Exception("Host is not an active actor. \
            #                           Use 'init_host' to make it alive.")

            if hasattr(klass, '_parallel') and klass._parallel:
                new_actor = ActorParallel(url, klass, obj)
                lock = new_actor.get_lock()
                self.locks[url] = lock
            else:
                new_actor = Actor(url, klass, obj)

            obj.proxy = Proxy(new_actor)

            self.launch_actor(url, new_actor)
            return Proxy(new_actor)

    def lookup(self, id):
        '''
        Gets a new proxy that references to the actor of this host
        identified by the given ID.

        This method can be called remotely synchronously.

        :param str. id: identifier of the actor you want.
        :return: :class:`~.Proxy` of the actor requiered.
        :raises: :class:`HostDown`  if the host is down.
        '''
        if not self.alive:
            raise HostDown()
        url = '%s://%s/%s' % (self.transport, self.host_url.netloc, id)
        if url in self.actors.keys():
            return Proxy(self.actors[url])
        else:
            raise NotFound()

    def shutdown(self):
        '''
        Stops the Host, stopping at the same time all its actors.
        Should be called at the end of its usage, to finish correctly
        all the connections and threads.
        When the actors stop running, they can't be started again and
        the host can't process new spawns. You might need to create a
        new host (:func:`create_host`).

        This method can't be called remotely.
        '''
        if self.alive:
            for interval_event in self.intervals.values():
                interval_event.set()

            for actor in self.actors.values():
                Proxy(actor).stop()

            for parall in self.pthreads.keys():
                parall.join()

            for thread in self.threads.keys():
                thread.join()

            # self.cleaner.set()

            self.locks.clear()
            self.actors.clear()
            self.threads.clear()
            self.pthreads.clear()
            self.running = False
            self.alive = False

            del util.hosts[self.url]
            if util.main_host.url == self.url:
                util.main_host = (util.hosts.values()[0] if util.hosts.values()
                                  else None)

    def lookup_url(self, url):
        '''
        Gets a proxy reference to the actor indicated by the URL in the
        parameters. It can be a local reference or a TCP direction.

        This method can be called remotely synchronously.

        :param srt. url: address that identifies an actor.
        :return: :class:`~.Proxy` of the actor requested.
        :raise: :class:`NotFound`, if the URL specified do not
            correspond to any actor in the host.
        :raises: :class:`HostDown`  if the host is down.
        '''
        if not self.alive:
            raise HostDown()
        aurl = urlparse(url)
        if self.is_local(aurl):
            if url not in self.actors.keys():
                raise NotFound()
            else:
                return Proxy(self.actors[url])
        else:
            raise Exception("TCPthing")
            # addrl = aurl.netloc.split(':')
            # addr = addrl[0],addrl[1]
            # if actors.has_key(addr):
            #     dispatcher = actors[addr]
            # else:
            #     dispatcher = self.tcp.get_dispatcher(addr)
            #     launch_actor(addr,dispatcher)
            # remote_actor = ActorRef(url,klass,dispatcher.channel)
            # return Proxy(remote_actor)

    def is_local(self, aurl):
        # '''Private method.
        # Tells if the address given is from this host.
        #
        # :param ParseResult aurl: address to analyze.
        # :return: (*Bool.*) If is local (**True**) or not (**False**).
        # '''
        return self.host_url.netloc == aurl.netloc

    def launch_actor(self, url, actor):
        # '''Private method.
        # This function makes an actor alive to start processing queries.
        #
        # :param str. url: identifier of the actor.
        # :param Actor actor: instance of the actor.
        # '''
        actor.run()
        self.actors[url] = actor
        self.threads[actor.thread] = url

    def init_host(self):
        '''
        This method creates an actor for the Host so it can spawn actors
        remotely. Called always from the init function of the host, so
        no need for calling this directly.
        '''
        if not self.running and self.alive:
            self.id = self.url
            host = Actor(self.url, Host, self)
            self.proxy = Proxy(host)
            self.launch_actor(self.url, host)
            self.running = True

    def signal_handler(self, signal, frame):
        '''
        This gets the signal of Ctrl+C and stops the host. It also ends
        the execution. Needs the invocation of :meth:`serve_forever`.

        :param signal: SIGINT signal interruption sent with a Ctrl+C.
        :param frame: the current stack frame. (not used)
        '''
        print 'You pressed Ctrl+C!'
        self.shutdown()
        self.serving = False

    def serve_forever(self):
        '''
        This allows the host to keep alive indefinitely so its actors
        can receive queries at any time.
        To kill the execution, press Ctrl+C.

        See usage example in :ref:`sample6`.
        '''
        if not self.alive:
            raise Exception("This host is already shutted down.")
        self.serving = True
        signal.signal(signal.SIGINT, self.signal_handler)
        print 'Press Ctrl+C to kill the execution'
        while self.serving:
            try:
                sleep(1)
            except Exception:
                pass
        print 'BYE!'

    def attach_interval(self, interval_id, interval_event):
        '''Registers an interval event to the host.'''
        self.intervals[interval_id] = interval_event

    def detach_interval(self, interval_id):
        '''Deletes an interval event from the host registry.'''
        del self.intervals[interval_id]

    def _dumps(self, param):
        '''
        Checks the parameters generating new proxy instances to avoid
        query concurrences from shared proxies.
        '''
        if isinstance(param, Proxy):
            return self.lookup_url(param.actor.url)
        elif isinstance(param, list):
            return [self._dumps(elem) for elem in param]
        elif isinstance(param, dict):
            new_dict = param
            for key in new_dict.keys():
                new_dict[key] = self._dumps(new_dict[key])
            return new_dict
        else:
            return param

    def _loads(self, param):
        '''
        Checks the return parameters generating new proxy instances to
        avoid query concurrences from shared proxies.
        '''
        if isinstance(param, Proxy):
            return self.lookup_url(param.actor.url)
        elif isinstance(param, list):
            return [self._loads(elem) for elem in param]
        elif isinstance(param, dict):
            new_dict = param
            for key in new_dict.keys():
                new_dict[key] = self._loads(new_dict[key])
            return new_dict
        else:
            return param

    def new_parallel(self, from_url, invoke, param):
        '''
        Register a new thread executing a parallel method.
        '''
        t = threading.Thread(target=invoke, args=param)
        t.start()
        self.pthreads[t] = from_url

    def do_clean(self):
        '''
        This function is called at intervals to delete the threads
        created for parallel methods that have already stopped.
        '''
        for t in self.pthreads.values():
            if not t.isAlive():
                del self.pthreads[pthr]
