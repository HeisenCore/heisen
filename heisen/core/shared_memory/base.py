import datetime
import string
import time
import socket
import random

from bson.json_util import dumps as bson_dumps
from bson.json_util import loads as bson_loads
import zmq

from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from zmq.utils.jsonapi import dumps
from zmq.utils.jsonapi import loads

from heisen.core.log import logger
from heisen.config import settings
from heisen.core import rpc_call


class Base(object):
    name = 'base'

    def __init__(self):
        self.instantiate_time = datetime.datetime.now()
        self.member_name = str(self.generate_unique_id())
        self.lock_time = None

        self.server_host = settings.ZMQ['HOST']
        self.pub_port = settings.ZMQ['PUB']
        self.rep_port = settings.ZMQ['REP']

        self.peers = []

        # Connection for REP/REQ pattern
        context = zmq.Context()
        self.rep_server = context.socket(zmq.REQ)
        self.rep_server.connect(
            "tcp://{0}:{1}".format(self.server_host, self.rep_port)
        )

        self.sign = ' |/\| '
        self._start_subscriber()
        self.send_info()
        reactor.callInThread(self.heartbeating)

    def _start_subscriber(self):
        logger.zmq('Start subscriber')
        context = zmq.Context()

        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect(
            "tcp://{0}:{1}".format(self.server_host, self.pub_port)
        )

        self.subscriber.setsockopt(zmq.SUBSCRIBE, self.name)
        worker_sub = deferToThread(self._listener)
        worker_sub.addErrback(log_error)

        logger.zmq("Start subscriber {0}...... .".format(self.name))

    def _listener(self):
        while True:
            string = self.subscriber.recv()

            if not string:
                continue

            message = string.split(self.sign)
            if len(message) != 2:
                continue

            data = loads(message[1])

            if data[0] == 'set_value':
                self.set_value(
                    messagedata[0],
                    data[1],
                    bson_loads(data[2])
                )

            elif data[0] == 'del_value':
                self.del_value(messagedata[0], data[1])

            elif data[0] == 'register':
                self.add_peer(bson_loads(data[1]))

            elif data[0] == 'alter_member':
                for member in self.registry:
                    if member['member_name'] == data[1]:
                        member['new_member'] = False

            if messagedata[0] == 'signaling':
                data = bson_loads(data)

                for func in self.signaling_funcs:
                    defer = deferToThread(func, *data)
                    defer.addErrback(to_log_error)

    def send_info(self, new_member=True):
        info = {
            'instantiate_time': self.instantiate_time,
            'member_name': self.member_name,
            'alive': True,
            'new_member': new_member,
            'host': self._get_host_ip(),
            'port': settings.RPC_PORT
            # 'sync': True,  # evaluate after instantiate
        }

        self.send_msg('register', 'controler', info)
        logger.zmq('Sending info: {0}'.format(info))

    def _get_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.server_host, self.pub_port))
        address = s.getsockname()[0]

        return address

    def add_peer(self, peer_info):
        peers = [peer['member_name'] for peer in self.peers]

        if peer_info['member_name'] not in peers:
            self.peers.append(peer_info)
            self.lock_time = datetime.datetime.now()
            self.send_info(new_member=False)
            logger.zmq('Receive & Rgister: {0}'.format(info))

        self.send_synchronizer()

    def send_synchronizer(self):
        self.peers.sort(
            key=lambda peer: peer['instantiate_time'],
            reverse=False
        )
        first_member = filter(lambda peer: peer['alive'], self.peers)[0]

        if first_member['member_name'] != self.member_name:
            return

        members = []
        for member in self.registry:
            if member['new_member'] and member['alive']:
                host = member['host']
                port = member['port']
                name = member['member_name']
                members.append((host, port, name))

        if not members:
            return

        data = []
        for attr in settings.TOPICS:
            data.append({attr: getattr(self, attr)})

        for member in members:
            result = rpc_call.self.main.load_attrs(data)

            self.alter_member(member[2])

        logger.zmq("Synchronizer result: {0}".format(result))

    def alter_member(self, member_name):
        self.send_msg('alter_member', 'controler', member_name)

    def del_value(self, attr, key):
        var = getattr(self, attr)
        del var[key]

    @process
    def set_value(self, attr, key, value):
        var = getattr(self, attr)
        var[key] = value

    def get_value(self, attr, key):
        return getattr(self, attr)[key]

    def generate_unique_id(self):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for i in range(6))

    def load_attrs(self, data):
        for doc in data:
            for k, v in doc.items():
                setattr(self, k, v)

    def retrive_attr(self, attr):
        return getattr(self, attr).copy()

    def retrive_attr_without_copy(self, attr):
        return getattr(self, attr)

    def send_msg(self, *args):
        """
            args[0] = function name
            args[1] = attribute name or topic name
            args[2] = key of dictionary | value of function
            args[3] = value of dictionary
        """
        if args[0] == 'set_value':
            arg = (args[0], args[2], bson_dumps(args[3]))

        elif args[0] == 'del_value':
            arg = (args[0], args[2])

        elif args[0] == 'register':
            arg = (args[0], bson_dumps(args[2]))

        elif args[0] == 'alter_member':
            arg = (args[0], args[2])

        msg = "{0}{1}{2}".format(args[1], self.sign, dumps(arg))
        self.rep_server.send(msg)
        self.rep_server.recv()

    def heartbeating(self):
        while True:
            time.sleep(settings.HEARTBEAT_TIME)

            for member in self.registry:
                try:
                    result = rpc_call.self.main.heartbeat()
                except:
                    member['alive'] = False

            logger.zmq('Heartbeat checking Done... .')


def log_error(failure):
    logger.error(str(failure))
