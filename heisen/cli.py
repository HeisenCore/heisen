#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from cliff.app import App as CliffApp
from cliff.commandmanager import CommandManager
from cliff.command import Command


class App(CliffApp):
    def __init__(self, manager):
        super(App, self).__init__(
            description='cliff demo app',
            version='0.1',
            command_manager=manager,
            deferred_help=True,
        )

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


class Run(Command):
    def take_action(self, parsed_args):
        from rpc.run import start_service
        start_service()


class Stop(Command):
    def take_action(self, parsed_args):
        from jsonrpclib import Server
        from socket import error
        from config.settings import RPC_PORT

        try:
            conn = Server('http://rostamkhAn!shoja:p4ssw0rdVahdaTi@localhost:{0}'.format(RPC_PORT))
            conn.main.stop()

        except error:
            print 'Core Services shutdown \t\t\t\t\t\t[OK]'


def main(argv=sys.argv[1:], manager=None):
    if manager is None:
        manager = CommandManager('')

    manager.add_command('run', Run)
    manager.add_command('stop', Stop)
    myapp = App(manager)
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
