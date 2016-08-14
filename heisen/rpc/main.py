from txjsonrpc.web.jsonrpc import JSONRPC

from heisen.rpc import loader
from heisen.config import settings
from heisen.core.log import logger


class CoreServices(JSONRPC):
    # reactor.callInThread(initial_executer, )

    def __init__(self):
        JSONRPC.__init__(self)
        self.logger = logger
        self.app_name = settings.APP_NAME

    def jsonrpc_methodHelp(self, method):
        method = self._getFunction(method)
        return getattr(method.im_class, 'documentation', '')

    def jsonrpc_list_methods(self):
        return self.methods
