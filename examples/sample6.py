'''
Self references sample. Actor id/proxy. + serve_forever
'''
from pyactor.context import set_context, create_host, sleep, serve_forever
from pyactor.client import ActorC


class Echo(ActorC):
    _tell = ['echo']
    _ask = []

    def __init__(self, msg):
        print 'ECHO created:', self.id, msg

    def echo(self, msg, sender):
        print msg, 'from:', sender.get_name(), 'at', sender.get_net()
        # print sender.get_id(), sender.get_url()


class Bot(ActorC):
    _tell = ['set_echo', 'say_hi']
    _ask = ['get_name', 'get_net']

    def __init__(self):
        self.greetings = ['hello', 'hi', 'hey', 'what`s up?']
        print "Bot created:", self.id
        self.host.hello()       # Tell methods are OK
        # self.echo = self.host.lookup('echo1')     # Can't do this
        # Don't make an ask query to self.host or self.proxy inside __init__
        # they won't respond, leading to a TimeoutError.

    def set_echo(self):
        self.echo = self.host.lookup('echo1')

    def get_name(self):
        return self.id

    def get_net(self):
        return self.url

    def say_hi(self):
        for salute in self.greetings:
            self.echo.echo(salute, self.proxy)


if __name__ == "__main__":
    set_context()
    h = create_host()
    e1 = h.spawn('echo1', Echo, ['yey!'])
    bot = h.spawn('bot1', Bot)
    bot.set_echo()
    bot.say_hi()

    sleep(1)
    serve_forever()
