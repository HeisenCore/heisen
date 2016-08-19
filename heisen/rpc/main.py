from txjsonrpc.web.jsonrpc import JSONRPC
from txjsonrpc import jsonrpclib

from heisen.rpc import loader
from heisen.config import settings
from heisen.core.log import logger


class Main(JSONRPC):
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

    def _ebRender(self, failure, id):
        if isinstance(failure.value, jsonrpclib.Fault):
            return failure.value

        # log.err(failure)

        message = failure.value.message
        code = self._map_exception(type(failure.value))
        logger.error(failure.getTraceback())

        message = '{}|{}'.format(
            failure.type.__name__,
            failure.getErrorMessage()
        )

        return jsonrpclib.Fault(code, message)
