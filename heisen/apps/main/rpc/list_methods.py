from twisted.internet import reactor

from heisen.rpc.base import RPCBase
from heisen.core.shared_memory import shared_memory
from heisen.core import rpc_call


class RPC(RPCBase):
    def run(self):
        raise ValueError()
        reactor.callFromThread(reactor.stop)
