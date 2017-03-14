'''
Basic host creation sample.
'''
from pyactor.context import set_context, create_host, sleep, shutdown
from pyactor.client import ActorC


class Echo(ActorC):
    _tell = ['echo']
    # _ask = []

    def __init__(self, msg, iddd):
        print 'ECHO init', self.id, msg, iddd

    def echo(self, msg):
        print msg


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo, ['sup'], {'iddd':'kkk'})
    e1.echo('hello there !!')

    sleep(1)
    shutdown()
