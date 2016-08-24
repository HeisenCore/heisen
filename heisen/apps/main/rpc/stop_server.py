from twisted.internet import reactor
from heisen.rpc.base import RPCBase
from heisen.core.log import logger


class RPC(RPCBase):
    def run(self):
        reactor.callFromThread(reactor.stop)
