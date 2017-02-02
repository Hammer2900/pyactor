import pika
import threading

from pyactor.util import RABBITU, RABBITP, RABBIT_IP, RABBIT_PORT


class Consumer(threading.Thread):
    ''' Consumer is an actor subthread that can be consuming a rabbit queue
    as complement communication between or to actors.
    :param func. on_message: callable to be execueted when a message is consumed
        from the queue.
    :param str. queue: nome of the queue the consumer will be consuming from.
    '''
    def __init__(self, on_message, queue):
        creden = pika.PlainCredentials(RABBITU, RABBITP)
        params = pika.ConnectionParameters(host=RABBIT_IP,
                                           port=int(RABBIT_PORT),
                                           credentials=creden)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.on_message = on_message
        self.queue = queue

        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(self.on_request, queue=queue, no_ack=True)

    def run(self):
        self.channel.start_consuming()

    def on_request(self, ch, method, props, body):
        self.on_message(body)
