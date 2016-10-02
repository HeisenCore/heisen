import os

import zmq

PUB_SERVER_PORT = os.environ.get('PUB_SERVER_PORT', 5556)
REP_SERVER_PORT = os.environ.get('REP_SERVER_PORT', 5575)


def start_server():
    context = zmq.Context()
    print 'Messaging Server starting............ .'

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

        print 'Sending message, {}'.format(message)

        # Pass message to all clients
        pub.send(message)


if __name__ == '__main__':
    start_server()
