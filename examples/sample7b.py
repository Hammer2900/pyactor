'''
Proxy references by parameter sample. Passing proxies to __init__.
The parameters passed to the spawn to initialize the actor instance are
always checked fro proxies. No need to add __init__ to _ref.
'''
from pyactor.context import set_context, create_host, sleep, shutdown
from pyactor.client import ActorC


class Echo(ActorC):
    _tell = ['echo', 'echo2', 'echo3']
    _ask = []
    _ref = ['echo', 'echo2', 'echo3']

    def echo(self, msg, sender):
        # print sender
        print msg, 'from:', sender.get_name()

    def echo2(self, msg, sndrs):
        for sender in sndrs:
            print msg, 'from:', sender.get_name()

    def echo3(self, msg, sndrs):
        for sender in sndrs.values():
            print msg, 'from:', sender.get_name()


class Bot(ActorC):
    _tell = ['set_echo', 'say_hi']
    _ask = ['get_name']
    _ref = ['set_echo']

    def __init__(self, echo):
        self.greetings = ['hello', 'hi', 'hey', 'what`s up?']
        self.echo = echo

    def get_name(self):
        return self.id

    def say_hi(self):
        for salute in self.greetings:
            self.echo.echo(salute, self.proxy)


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo)
    bot = h.spawn('bot1', Bot, [e1])
    bot2 = h.spawn('bot2', Bot, [e1])
    bot.say_hi()
    sleep(1)
    e1.echo2('hello there!', [bot2])
    e1.echo3('hello there!!', {'bot1': bot, 'bot2': bot2})

    sleep(1)
    shutdown()
