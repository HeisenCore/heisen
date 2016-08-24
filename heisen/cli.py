#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from cliff.app import App as CliffApp
from cliff.commandmanager import CommandManager
from cliff.command import Command

from heisen.core.log import logger
from heisen.config import settings
from heisen.utils.module import load_module


class App(CliffApp):
    def __init__(self, manager):
        super(App, self).__init__(
            description='Heisen Cli Interface',
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


def main(argv=sys.argv[1:], manager=None):
    manager = CommandManager('')

    get_commands(settings.HEISEN_BASE_DIR, manager)

    if getattr(settings, 'BASE_DIR', None):
        get_commands(settings.BASE_DIR, manager)

    # manager.add_command('run', Run)
    # manager.add_command('stop', Stop)
    myapp = App(manager)
    return myapp.run(argv)


def get_commands(path, manager):
    command_dir = os.path.join(path, 'commands')
    if not os.path.isdir(command_dir):
        return

    for command_file in os.listdir(command_dir):
        if not command_file.endswith('.py'):
            continue

        command_name = command_file.replace('.py', '')
        command = load_module(command_name, command_dir)

        manager.add_command(command_name, command.Command)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
