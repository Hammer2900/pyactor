'''
Proxy references by parameter sample.
'''
from pyactor.context import create_host

from time import sleep


class Echo:
    _tell = ['echo', 'echo2', 'echo3']
    _ask = []
    _ref = ['echo', 'echo2', 'echo3']

    def echo(self, msg, sender):
        print msg, 'from:', sender.get_name().get(), id(sender)

    def echo2(self, msg, sndrs):
        for sender in sndrs:
            print msg, 'from:', sender.get_name().get(), id(sender)

    def echo3(self, msg, sndrs):
        for sender in sndrs.values():
            print msg, 'from:', sender.get_name().get(), id(sender)


class Bot:
    _tell = ['set_echo', 'say_hi']
    _ask = ['get_name']
    _ref = ['get_name']

    def __init__(self):
        self.greetings = ['hello', 'hi', 'hey', 'what`s up?']

    def set_echo(self):
        self.echo = self.host.lookup('echo1').get()

    def get_name(self):
        return self.id

    def say_hi(self):
        for salute in self.greetings:
            self.echo.echo(salute, self.proxy)


h = create_host()
e1 = h.spawn('echo1', Echo)
bot = h.spawn('bot1', Bot)
bot2 = h.spawn('bot2', Bot)
bot.set_echo()
bot2.set_echo()
bot.say_hi()
e1.echo2('hello there!!', [bot2])
e1.echo3('hello there!!', {'bot1': bot, 'bot2': bot2})

sleep(1)
h.shutdown()
