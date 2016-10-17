import os
import logging

import zmq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


PUB_SERVER_PORT = os.environ.get('PUB_SERVER_PORT', 5556)
REP_SERVER_PORT = os.environ.get('REP_SERVER_PORT', 5575)


def start_server():
    context = zmq.Context()
    logging.info('Messaging Server starting............ .')

    # Binding publisher server side
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:{0}".format(PUB_SERVER_PORT))

    # Binding Replier server side
    rep = context.socket(zmq.REP)
    rep.bind("tcp://*:{0}".format(REP_SERVER_PORT))

    while True:
        # Get message from clients
        message = rep.recv()

        # Replier answer
        rep.send('recived')

        logging.info('Sending message, {}'.format(message))

        # Pass message to all clients
        pub.send(message)


if __name__ == '__main__':
    start_server()
