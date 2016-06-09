"""
Samples requests::

    msg = TellRequest(TELL,'echo',[],url)
    msg = AskRequest(ASK,'echo',[],future_channel,url)
    msg = AskResponse(result)
    msg = FutureRequest(FUTURE,'get_x',[],'on_result',future_channel,url_to,url_from)

Defined constants:
    FROM, TO, TYPE, METHOD, PARAMS, FUTURE, ASK, TELL, SRC

"""
from threading import current_thread
import collections

FROM = 0
TO = 1
TYPE = 2
METHOD = 3
PARAMS = 4
FUTURE = 5
ASK = 6
TELL = 7
SRC = 8

host = None
def get_host():
    return host
def get_current():
    if host:
        current = current_thread()
        if host.threads.has_key(current):
            return host.actors[host.threads[current]]
        elif host.pthreads.has_key(current):
            return host.actors[host.pthreads[current]]
def get_lock():
    if host:
        url = None
        current = current_thread()
        if host.threads.has_key(current):
            url = host.threads[current]
        elif host.pthreads.has_key(current):
            url = host.pthreads[current]
        if host.locks.has_key(url):
            # print "At locks",url
            lock = host.locks[url]
            # print lock
            return lock

class Timeout(Exception):pass

class AlreadyExists(Exception):pass
class NotFound(Exception):pass

TellRequest = collections.namedtuple('TellRequest', 'type method params to_url')
#class TellRequest (collections.namedtuple('TellRequest', 'type method params to_url')):
'''
A namedtuple for the tell requests.
'''
AskRequest = collections.namedtuple('AskRequest', 'type method params channel to_url')
'''
A namedtuple for the ask requests.
'''
AskResponse = collections.namedtuple('AskResponse', 'result')
'''
A namedtuple for the responses of the requests :class:`AskRequest`.
'''
FutureRequest = collections.namedtuple('FutureRequest', 'type method params callback channel to_url from_url')
'''
A namedtuple for the future requests.
'''

#global AskRequest, TellRquest, AskResponse, FutureRequest
