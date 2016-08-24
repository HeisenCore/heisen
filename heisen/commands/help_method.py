from pprint import pprint

from cliff.command import Command as CliffCommand

from heisen.core.log import logger
from heisen.core import rpc_call


class Command(CliffCommand):
    def get_parser(self, prog_name):
        parser = super(Command, self).get_parser(prog_name)
        parser.add_argument('method_name', nargs='?')
        return parser

    def take_action(self, parsed_args):
        print rpc_call.self.help(parsed_args.method_name)
