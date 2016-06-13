'''
Sync/async queries sample.
'''
from pyactor.context import create_host

from time import sleep


class Echo:
    _tell = ['echo', 'bye']
    _ask = ['say_something']

    def echo(self, msg):
        print msg

    def bye(self):
        print 'bye'

    def say_something(self):
        return 'something'

h = create_host()
e1 = h.spawn('echo1', Echo)
e1.echo('hello there !!')
e1.bye()

print e1.say_something().get()

sleep(1)
h.shutdown()
