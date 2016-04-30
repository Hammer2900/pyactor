'''
Self references sample. Actor id/proxy. + serve_forever
'''
from pyactor.context import init_host, serve_forever
from time import sleep


class Echo:
    _tell =['echo']
    _ask = []
    def echo(self,msg,sender):
        print msg,'from:',sender.get_name().get()

class Bot:
    _tell =['set_echo','say_hi']
    _ask = ['get_name']
    def __init__(self):
        self.greetings = ['hello','hi','hey','what`s up?']
    def set_echo(self):
        self.echo = self.host.lookup('echo1').get()
    def get_name(self):
        return self.id
    def say_hi(self):
        for salute in self.greetings:
            self.echo.echo(salute,self.proxy)


h = init_host()
e1 = h.spawn('echo1',Echo).get()
bot = h.spawn('bot1',Bot).get()
bot.set_echo()
bot.say_hi()

sleep(1)
serve_forever()
