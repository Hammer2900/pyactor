'''
Remote example with registry. CLIENT 2
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, Host

from s4_registry import NotFound


class Server(object):
    _ask = {'add', 'wait_a_lot'}
    _tell = ['substract']

    def add(self, x, y):
        return x + y

    def substract(self, x, y):
        print 'subtract', x - y

    def wait_a_lot(self):
        sleep(2)
        return 'ok'


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1777')

    registry = host.lookup_url('http://127.0.0.1:1277/regis', 'Registry',
                               's4_registry')
    remote_host = registry.lookup('host1')

    server = remote_host.spawn('server', 's3_client/Server')
    z = server.add(6, 7)
    print z
    server.substract(6, 5)
    t = server.add(8, 7)
    print t

    try:
        registry.unbind('None')
    except NotFound:
        print "Cannot unbind this object: is not in the registry."

    host.shutdown()
