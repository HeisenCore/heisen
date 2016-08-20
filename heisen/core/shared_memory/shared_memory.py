import datetime
import time
import socket
from base64 import b64encode
from os import urandom

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


class SharedMemory(object):
    def __init__(self):
        self.instantiate_time = datetime.datetime.now()
        self.member_name = str(self.generate_unique_id())
        self.lock_time = None
        self.signaling_funcs = []

        self.pub_sub_host = settings.PUB_REP_HOST
        self.pub_sub_port = settings.PUB_PORT
        self.rep_req_host = settings.PUB_REP_HOST
        self.rep_req_port = settings.REP_PORT

        # Initiate consumer data listener
        self.topics = {}
        for i in settings.TOPICS:
            self.topics[i] = {}

        # create dict "key, value" from items(topics)
        for key in settings.TOPICS:
            setattr(self, key, dict())

        # Register all client
        self.registry = []

        # Connection for REP/REQ pattern
        context = zmq.Context()
        self.send_socket = context.socket(zmq.REQ)
        self.send_socket.connect(
            "tcp://{0}:{1}".format(self.rep_req_host, self.rep_req_port)
        )

        self.sign = ' |/\| '
        self.__sync_subscribe()
        self.send_info()
        reactor.callInThread(self.heartbeating)

    def add_signal(self, func):
        if func in self.signaling_funcs:
            name = func.func_name
            msg = "'{}' function exist's in the signal list.".format(name)
            logger.error(msg)
        else:
            self.signaling_funcs.append(func)

    def send_info(self, new_member=True):
        info = {
            'instantiate_time': self.instantiate_time,
            'member_name': self.member_name,
            'alive': True,
            'new_member': True,
            'host': self._get_host_ip(),
            'port': settings.RPC_PORT
            # 'sync': True,  # evaluate after instantiate
        }
        if not new_member:
            info['new_member'] = False

        self.send_msg('register', 'controler', info)
        logger.zmq('Sending info: {0}'.format(info))

    def _get_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.pub_sub_host, self.pub_sub_port))
        address = s.getsockname()[0]

        return address

    def register_members(self, info):
        members_name = []
        for doc in self.registry:
            members_name.append(doc['member_name'])

        if info['member_name'] not in members_name:
            self.registry.append(info)
            self.lock_time = datetime.datetime.now()
            self.send_info(new_member=False)
            logger.zmq('Receive & Rgister: {0}'.format(info))

        self.send_synchronizer()

    def heartbeating(self):
        while True:
            time.sleep(settings.HEARTBEAT_TIME)

            for member in self.registry:
                try:
                    result = rpc_call.self.main.heartbeat()
                    if not result.get('result', None):
                        member['alive'] = False
                except:
                    member['alive'] = False
            logger.zmq('Heartbeat checking Done... .')

    def send_synchronizer(self):
        self.registry.sort(
            key=lambda item: item['instantiate_time'],
            reverse=False
        )

        first_member = self.registry[0]
        if not self.registry[0]['alive']:
            first_member = self.registry[1]

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
            if result.get('result', None):
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
        return b64encode(urandom(9))

    def load_attrs(self, data):
        for doc in data:
            for k, v in doc.items():
                setattr(self, k, v)

    def retrive_attr(self, attr):
        return getattr(self, attr).copy()

    def retrive_attr_without_copy(self, attr):
        return getattr(self, attr)

    def __sync_subscribe(self):
        logger.zmq('Start subscriber')
        context = zmq.Context()

        for key in self.topics.keys():
            self.topics[key] = context.socket(zmq.SUB)
            self.topics[key].connect(
                "tcp://{0}:{1}".format(self.pub_sub_host, self.pub_sub_port)
            )
            self.topics[key].setsockopt(zmq.SUBSCRIBE, key)
            worker_sub = deferToThread(self.infinity_loop, self.topics[key])

            logger.zmq("Start subscriber {0}...... .".format(key))
            worker_sub.addErrback(to_log_error)

    def infinity_loop(self, obj):
        while True:
            string = obj.recv()

            if string:
                messagedata = string.split(self.sign)
                if len(messagedata) == 2:
                    data = loads(messagedata[1])

                    if data[0] == 'set_value':
                        self.set_value(
                            messagedata[0],
                            data[1],
                            bson_loads(data[2])
                        )

                    elif data[0] == 'del_value':
                        self.del_value(messagedata[0], data[1])

                    elif data[0] == 'register':
                        self.register_members(bson_loads(data[1]))

                    elif data[0] == 'alter_member':
                        for member in self.registry:
                            if member['member_name'] == data[1]:
                                member['new_member'] = False

                    if messagedata[0] == 'signaling':
                        data = bson_loads(data)

                        for func in self.signaling_funcs:
                            defer = deferToThread(func, *data)
                            defer.addErrback(to_log_error)

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
        self.send_socket.send(msg)
        logger.zmq('Sending..')
        self.send_socket.recv()


def to_log_error(failure):
    logger.error(str(failure))
