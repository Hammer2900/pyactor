'''
Intervals sample
@author: Daniel Barcelona Pons
'''
from pyactor.context import (set_context, create_host, sleep,
                             interval_host, later)


class Registry(object):
    _ask = []
    _tell = ['hello', 'init_start']

    def init_start(self):
        self.interval1 = interval_host(self.host, 1, self.hello)
        later(10, self.stop_interval)

    def stop_interval(self):
        self.interval1.set()

    def hello(self):
        print 'Hello'


if __name__ == "__main__":
    set_context()
    host = create_host()
    registry = host.spawn('1', Registry)
    registry.init_start()
    # host.serve_forever()
    sleep(11)
    host.shutdown()
