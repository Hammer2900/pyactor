'''
Timeout smaple.
'''
from pyactor.context import create_host
from pyactor.util import TimeoutError

from time import sleep


class Echo:
    _tell = ['echo', 'bye']
    _ask = ['say_something']

    def echo(self, msg):
        print msg

    def bye(self):
        print 'bye'

    def say_something(self):
        sleep(2)
        return 'something'

h = create_host()
e1 = h.spawn('echo1', Echo)
e1.echo('hello there !!')
e1.bye()

try:
    x = e1.say_something().get(1)
except TimeoutError:
    print 'timeout catched'
sleep(1)
h.shutdown()
