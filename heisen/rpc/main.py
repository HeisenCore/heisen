from txjsonrpc.web import jsonrpc

from heisen.rpc import loader


class CoreServices(jsonrpc.JSONRPC):
    # reactor.callInThread(initial_executer, )

    def jsonrpc_methodHelp(self, method):
        method = self._getFunction(method)
        return getattr(method.im_class, 'documentation', '')

    def jsonrpc_list_methods(self):
        return self.methods
