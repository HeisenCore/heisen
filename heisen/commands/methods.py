from pprint import pprint

from cliff.command import Command as CliffCommand

from heisen.core import rpc_call


class Command(CliffCommand):
    def take_action(self, parsed_args):
        pprint(rpc_call.self.list_methods())
