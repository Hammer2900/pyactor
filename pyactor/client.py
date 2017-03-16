from uuid import uuid4


from context import interval, later


class MetaActor(type):
    def __new__(mcs, name, bases, dct):
        if not 'ActorC' in name:
            if dct.has_key('__init__'):
                dct['_initial'] = dct['__init__']
                del dct['__init__']
            else:
                dct['_initial'] = lambda self: None

        return type.__new__(mcs, name, bases, dct)


class ActorC(object):
    # __metaclass__ = MetaActor

    def init_actor(self):
        pass

    def new_interval(self, time, method, *args, **kwargs):
        try: self.__intervals
        except AttributeError:
            self.__intervals = {}
        iid = self.id + '_interval_' + str(uuid4())
        self.__intervals[iid] = interval(self.host, time, self.proxy,
                                         method, *args, **kwargs)
        return iid

    def stop_interval(self, interval_id, v=False):
        try:
            self.__intervals[interval_id].set()
            del self.__intervals[interval_id]
            if v:
                print 'stopped', interval_id
        except:
            print 'no such interval', interval_id

    def stop_all_intervals(self):
        for interval in self.__intervals.values():
            interval.set()
        self.__intervals = {}

    def new_later(self, timeout, method, *args, **kwargs):
        return later(timeout, self.proxy, method, *args, **kwargs)
