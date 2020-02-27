"""
Basic remote example sending tell messages. CLIENT, stress
@author: Daniel Barcelona Pons
"""
from pyactor.context import set_context, create_host, shutdown


if __name__ == '__main__':
    set_context()
    host = create_host("http://127.0.0.1:1679")

    e1 = host.lookup_url("http://127.0.0.1:1277/echo1", 'Echo', 's1_server')

    i = 0
    while i < 1000:
        e1.echo("Hi there!")    # TELL message
        e1.echo("See ya!")
        # sleep(1)
        i += 1

    shutdown()
