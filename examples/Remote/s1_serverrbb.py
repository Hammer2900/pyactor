'''
Basic remote example sending tell messages. SERVER
@author: Daniel Barcelona Pons
'''
from pyactor.context import \
    set_context, create_host, setRabbitCredentials, serve_forever


class Echo(object):
    _tell = ['echo']
    _ask = []

    def echo(self, msg):
        print msg

if __name__ == "__main__":
    # setRabbitCredentials('daniel', 'passs')
    set_context()
    host = create_host('amqp://127.0.0.1:1277/')

    e1 = host.spawn('echo1', Echo)
    serve_forever()
