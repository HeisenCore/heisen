from twisted.internet import reactor

from heisen.rpc.base import RPCBase


class RPC(RPCBase):
    def run(self):
        raise ValueError()
        reactor.callFromThread(reactor.stop)
