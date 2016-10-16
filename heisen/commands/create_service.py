from cliff.command import Command as CliffCommand

from heisen.core.log import logger

from heisen.systems.service import manage


class Command(CliffCommand):
    def take_action(self, parsed_args):
        manage.create_config()
