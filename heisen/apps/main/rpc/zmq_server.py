import zmq

from heisen.core.log import logger
from heisen.config import settings
from heisen.rpc.base import RPCBase


class RPC(RPCBase):
    documentation = """
        Publisher & replier server

        e.g:
        main.pub_rep() > object

        Keyword arguments:

        ACL:
            TODO:
    """

    def run(self):
        # Initiate context
        context = zmq.Context()
        logger.debug('Messaging Server starting............ .')

        # Binding publisher server side
        pub = context.socket(zmq.PUB)
        pub.bind("tcp://*:{0}".format(settings.PUB_PORT))

        # Binding Replier server side
        rep = context.socket(zmq.REP)
        rep.bind("tcp://*:{0}".format(settings.REP_PORT))

        while True:
            # Get message from clients
            message = rep.recv()

            # Replier answer
            rep.send('recived')

            # Pass message to all clients
            pub.send(message)

        return True
