import datetime
import socket

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
            lambda member: member['alive'], self.members.values()
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

    def __init__(self):
        super(Register, self).__init__()
        self.members = {}

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
        for name, member in self.members.items():
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
            self.members[new_member['member_name']] = new_member

        if new_member['member_name'] in self.members:
            return

        self.members[new_member['member_name']] = new_member

        connection_info = (
            new_member['host'], new_member['port'],
            new_member['auth_username'], new_member['auth_password']
        )
        rpc_call.add_server(new_member['app_name'], connection_info)

        self.lock_time = datetime.datetime.now()

        if self._first_member:
            self._send_message('renew_members', self.members)

        logger.zmq('Added new member: {0}'.format(new_member))

    def renew_members(self, members):
        self.members = members
