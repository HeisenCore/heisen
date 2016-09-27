from twisted.internet import reactor

from heisen.rpc.base import RPCBase
# from heisen.core.shared_memory import memory
from heisen.core import rpc_call


class RPC(RPCBase):
    signals = [
        ('before', 'main.list_methods')
    ]
    def run(self):
        memory.set_value('shared_memory', '12213123', {1:1})

        return memory.get_value('shared_memory', '12213123')
