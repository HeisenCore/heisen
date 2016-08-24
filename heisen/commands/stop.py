from cliff.command import Command as CliffCommand

import os
from heisen.core.log import logger


class Command(CliffCommand):
    def take_action(self, parsed_args):
        from jsonrpclib import Server
        from socket import error
        from heisen.config import settings

        try:
            conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(settings.RPC_PORT))
            conn.main.stop()

        except error:
            print 'Core Services shutdown \t\t\t\t\t\t[OK]'
