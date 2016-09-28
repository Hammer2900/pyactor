'''
Remote example with a registry. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import set_context, create_host


class NotFound(Exception):
    pass


class Registry:
    _ask = ['get_all', 'bind', 'lookup', 'unbind']
    _async = []
    _ref = ['get_all', 'bind', 'lookup']

    def __init__(self):
        self.actors = {}

    def bind(self, name, actor):
        self.actors[name] = actor

    def unbind(self, name):
        if name in self.actors.keys():
            del self.actors[name]
        else:
            raise NotFound()

    def lookup(self, name):
        return self.actors[name]

    def get_all(self):
        return self.actors.values()


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:1277/')

    registry = host.spawn('regis', Registry)

    print 'host listening at port 1277'

    host.serve_forever()
