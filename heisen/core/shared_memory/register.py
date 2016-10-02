import datetime
import socket
from functools import partial

from jsonrpclib.request import Connection
from twisted.internet.task import LoopingCall

from heisen.core.log import logger
from heisen.config import settings
from heisen.core import rpc_call
from heisen.core.shared_memory.base import Base


class Register(Base):
    topic = 'controler'

    @property
    def _first_member(self):
        alive_members = filter(
            lambda member: member['alive'], self._members.values()
        )
        sorted_alive_members = sorted(
            alive_members,
            key=lambda member: member['instantiate_time'],
            reverse=False
        )
        first_alive_member = sorted_alive_members[0]

        return first_alive_member['member_name'] == self.member_name

    @property
    def _host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.server_host, self.pub_port))
        address = s.getsockname()[0]

        return address

    @property
    def members(self):
        return self._members

    def __init__(self, new_member_callbacks=None):
        super(Register, self).__init__()
        self._members = {}
        self._new_member_callbacks = new_member_callbacks

        if self._new_member_callbacks is None:
            self._new_member_callbacks = []

        self._new_member_callbacks.insert(0, self._renew_members)

        self._tell_others()
        LoopingCall(self._heartbeat).start(settings.HEARTBEAT_TIME)

    def _tell_others(self):
        member = {
            'instantiate_time': self.instantiate_time,
            'member_name': self.member_name,
            'app_name': settings.APP_NAME,
            'alive': True,
            'synced': False,

            'host': self._host_ip,
            'port': settings.RPC_PORT,
            'auth_username': None,
            'auth_password': None,
        }

        if settings.CREDENTIALS:
            username, passowrd = settings.CREDENTIALS[0]
            member['auth_username'] = username
            member['auth_password'] = passowrd

        self._send_message('add_member', member)

    def _heartbeat(self):
        for name, member in self._members.items():
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

    def add_member(self, new_member):
        if new_member['member_name'] == self.member_name:
            self._members[new_member['member_name']] = new_member

        if new_member['member_name'] in self._members:
            return

        self._members[new_member['member_name']] = new_member

        connection_info = (
            new_member['host'], new_member['port'],
            new_member['auth_username'], new_member['auth_password']
        )
        rpc_call.add_server(new_member['app_name'], connection_info)

        self.lock_time = datetime.datetime.now()

        if self._first_member:
            for callback in self._new_member_callbacks:
                callback()

        logger.zmq('Added new member: {0}'.format(new_member))

    def _renew_members(self):
        self._send_message('renew_members', self._members)

    def renew_members(self, members):
        self._members = members
