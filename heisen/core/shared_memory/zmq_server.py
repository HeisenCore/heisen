import zmq

from heisen.core.log import logger
from heisen.config import settings


def start_server():
    context = zmq.Context()
    logger.zmq('Messaging Server starting............ .')

    # Binding publisher server side
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:{0}".format(settings.PUB_SERVER_PORT))

    # Binding Replier server side
    rep = context.socket(zmq.REP)
    rep.bind("tcp://*:{0}".format(settings.REP_SERVER_PORT))

    while True:
        # Get message from clients
        message = rep.recv()

        # Replier answer
        rep.send('recived')

        logger.zmq('Sending message, {}'.format(message))

        # Pass message to all clients
        pub.send(message)
