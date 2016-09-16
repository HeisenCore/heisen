import datetime
import string
import time
import socket
import random

import zmq
from jsonrpclib.request import Connection
from bson.json_util import dumps as bson_dumps
from bson.json_util import loads as bson_loads
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from heisen.core.log import logger
from heisen.config import settings
from heisen.core import rpc_call


def process(func):
    def execute(*args, **kwargs):
        if args[0].lock_time:
            now = datetime.datetime.now()
            lock = args[0].lock_time + datetime.timedelta(seconds=settings.WAIT_MEMBER)
            if now < lock:
                time.sleep(settings.WAIT_MEMBER)
                logger.zmq(
                    'Lock time: {0} | {1} | {2}'.format(
                        args[0].member_name,
                        args[1:],
                        kwargs
                    )
                )
        return func(*args, **kwargs)

    return execute


class Base(object):
    base_topic = 'base'

    @property
    def _first_member(self):
        sorted(
            self.members.values(),
            key=lambda member: member['instantiate_time'],
            reverse=False
        )
        first_member = filter(lambda member: member['alive'], self.members)[0]

        return first_member['member_name'] == self.member_name

    @property
    def _host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.server_host, self.pub_port))
        address = s.getsockname()[0]

        return address

    def __init__(self):
        self.instantiate_time = datetime.datetime.now()
        self.member_name = str(self.generate_unique_id())
        self.lock_time = None

        self.server_host = settings.ZMQ['HOST']
        self.pub_port = settings.ZMQ['PUB']
        self.rep_port = settings.ZMQ['REP']

        self.members = {}

        # Connection for REP/REQ pattern
        context = zmq.Context()
        self.rep_server = context.socket(zmq.REQ)
        self.rep_server.connect(
            "tcp://{0}:{1}".format(self.server_host, self.rep_port)
        )

        self.sign = ' |/\| '
        self._start_subscriber()
        self.send_app_info()
        LoopingCall(self.heartbeating).start(settings.HEARTBEAT_TIME)

    def _start_subscriber(self):
        context = zmq.Context()

        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect(
            "tcp://{0}:{1}".format(self.server_host, self.pub_port)
        )

        self.subscriber.setsockopt(zmq.SUBSCRIBE, self.base_topic)
        if hasattr(self, 'topic'):
            self.subscriber.setsockopt(zmq.SUBSCRIBE, self.topic)

        worker_sub = deferToThread(self._listener)
        worker_sub.addErrback(log_error)

        logger.zmq("Start subscriber {0}...... .".format(self.name))

    def _listener(self):
        while True:
            try:
                string = self.subscriber.recv()
                topic, _, message = string.split(self.sign)
                message = bson_loads(message)

                handler_name = '_process_message_{}'.format(topic)
                if hasattr(self, handler_name):
                    getattr(self, handler_name)(message)
                else:
                    logger.zmq('Ignoring message with unknown topic, {}'.format(string))

                self._process_message(string)
            except Exception as e:
                logger.exception(e)

    def _process_message_base(self, message):
        if message['command'] == 'register':
            self.add_member(message['key'])

        elif message['command'] == 'alter_member':
            if message['key'] in self.members.values():
                self.members[message['key']]['new_member'] = False

    def send_app_info(self, new_member=True):
        info = {
            'instantiate_time': self.instantiate_time,
            'member_name': self.member_name,
            'app_name': settings.APP_NAME,
            'alive': True,
            'new_member': new_member,

            'host': self._host_ip,
            'port': settings.RPC_PORT,
            'auth_username': None,
            'auth_password': None,
            # 'sync': True,  # evaluate after instantiate
        }

        if settings.CREDENTIALS:
            username, passowrd = settings.CREDENTIALS[0]
            info['auth_username'] = username
            info['auth_password'] = passowrd

        self.send_msg('controler', 'register', info)

    def add_member(self, new_member):
        if new_member['member_name'] in self.members:
            return

        connection_info = (
            new_member['host'], new_member['port'],
            new_member['auth_username'], new_member['auth_password']
        )
        rpc_call.add_server(new_member['app_name'], connection_info)

        self.members[new_member['member_name']] = new_member
        self.lock_time = datetime.datetime.now()

        if self._first_member:
            self.send_synchronizer(new_member, connection_info)

        logger.zmq('Added new member: {0}'.format(new_member))

    def send_synchronizer(self, new_member, connection_info):
        data = {}
        for attr in ['members']:
            data[attr] = getattr(self, attr)

        rpc = Connection('heisen', 'zmq', *connection_info)
        result = rpc.connection.main.load_attrs(data)

        self.alter_member(new_member[2])

        logger.zmq("Synchronizer result: {0}".format(result))

    def alter_member(self, member_name):
        self.send_msg('controler', 'alter_member', member_name)

    def generate_unique_id(self):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for i in range(6))

    def send_msg(self, topic, command, key=None, value=None):
        """
            args[0] = function name
            args[1] = attribute name or topic name
            args[2] = key of dictionary | value of function
            args[3] = value of dictionary
        """
        message = {'command': command, 'key': key, 'value': value}
        msg = "{0}{1}{2}".format(topic, self.sign, bson_dumps(message))
        logger.zmq('Sending message {}'.format(msg))
        self.rep_server.send(msg)
        self.rep_server.recv()

    def heartbeating(self):
        for member in self.members:
            try:
                connection_info = (
                    member['host'], member['port'],
                    member['auth_username'], member['auth_password']
                )
                rpc = Connection('heisen', 'zmq', *connection_info)
                rpc.connection.main.heartbeat()
            except Exception as e:
                member['alive'] = False
                logger.exception(e)


def log_error(failure):
    logger.error(failure.getTraceback())


class SharedMemory(Base):
    topic = 'shared_memory'

    def _process_message_shared_memory(self, message):
        if message['command'] == 'set_value':
            self.set_value(
                message['command'], message['key'], message['value'],
            )

        elif message['command'] == 'del_value':
            self.del_value(message['key'])

    def del_value(self, attr, key):
        var = getattr(self, attr)
        del var[key]

    @process
    def set_value(self, attr, key, value):
        var = getattr(self, attr)
        var[key] = value

    def get_value(self, attr, key):
        return getattr(self, attr)[key]

    def load_attrs(self, data):
        for doc in data:
            for k, v in doc.items():
                setattr(self, k, v)

    def retrive_attr(self, attr):
        return getattr(self, attr).copy()

    def retrive_attr_without_copy(self, attr):
        return getattr(self, attr)
