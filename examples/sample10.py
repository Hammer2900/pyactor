'''
Intervals sample
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host, sleep, shutdown
from pyactor.client import ActorC


class Registry(ActorC):
    _ask = []
    _tell = ['hello', 'init_start', 'stop_interval']
    # _ref = ['hello']

    def init_start(self):
        self.interval1 = self.new_interval(1, "hello", "you")
        # print self.interval1
        self.new_later(5, "stop_interval", self.interval1, True)

    # def end_interval(self, iid):
    #     print "stopping interval"
    #     self.stop_interval(iid)

    def hello(self, msg):
        print self.id, 'Hello', msg


if __name__ == "__main__":
    N = 10   # 10000

    set_context()
    host = create_host()
    registry = list()
    for i in xrange(0, N):
        registry.append(host.spawn(str(i), Registry))

    for i in xrange(0, N):
        registry[i].init_start()

    sleep(8)
    shutdown()
