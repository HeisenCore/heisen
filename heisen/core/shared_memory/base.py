import abc
import datetime

import zmq
from bson.json_util import dumps, loads
from twisted.internet.threads import deferToThread

from heisen.core.log import logger
from heisen.config import settings
from heisen.utils.utils import unique_id


class Base(object):
    __metaclass__ = abc.ABCMeta

    sign = ' |/\| '

    def __init__(self):
        self.instantiate_time = datetime.datetime.now()
        self.member_name = unique_id()
        self.lock_time = None

        self.server_host = settings.ZMQ['HOST']
        self.pub_port = settings.ZMQ['PUB']
        self.rep_port = settings.ZMQ['REP']

        # Connection for REP/REQ pattern
        context = zmq.Context()
        self.rep_server = context.socket(zmq.REQ)
        self.rep_server.connect(
            "tcp://{0}:{1}".format(self.server_host, self.rep_port)
        )

        self._start_subscriber()

    def _start_subscriber(self):
        context = zmq.Context()

        self.subscriber = context.socket(zmq.SUB)
        server_addr = "tcp://{0}:{1}".format(self.server_host, self.pub_port)
        self.subscriber.connect(server_addr)

        self.subscriber.setsockopt(zmq.SUBSCRIBE, self.topic)
        deferToThread(self._listener)

        logger.zmq("Started subscriber to {} with topic '{}'".format(
            server_addr, self.topic
        ))

    def _listener(self):
        while True:
            try:
                string = self.subscriber.recv()
                logger.zmq('Received message {}'.format(string))
                topic, message = string.split(self.sign)
                message = loads(message)

                getattr(self, message['command'])(*message['args'])
            except Exception as e:
                logger.exception(e)

    def _send_message(self, command, *args):
        msg = "{0}{1}{2}".format(
            self.topic,
            self.sign,
            dumps({'command': command, 'args': args})
        )
        logger.zmq('Sending message {}'.format(msg))

        self.rep_server.send(msg)
        self.rep_server.recv()
