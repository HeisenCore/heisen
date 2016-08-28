import inspect
import os
from txjsonrpc.web.jsonrpc import JSONRPC
from txjsonrpc import jsonrpclib

from heisen.rpc import loader
from heisen.config import settings
from heisen.core.log import logger
from heisen.utils.module import load_module

class Main(JSONRPC):

    def __init__(self):
        JSONRPC.__init__(self)
        self.logger = logger
        self.app_name = settings.APP_NAME

        self._load()

    def _load(self):
        self.heisen_project = loader.Project(settings.HEISEN_BASE_DIR)
        self._add_subhandlers(self.heisen_project.apps)

        if hasattr(settings, 'BASE_DIR'):
            self.main_project = loader.Project(settings.BASE_DIR)
            self._add_subhandlers(self.main_project.apps)
        else:
            self.main_project = None

    def _add_subhandlers(self, apps):
        for component, klass in apps.items():
            try:
                self.putSubHandler(component, klass)
            except Exception as e:
                logger.exception(e, 'service')
                logger.service("App {} failed to register".format(component))

    def jsonrpc_help(self, method):
        method = self._getFunction(method)

        method_class = method.im_self
        method_docs = method_class.documentation

        method_name = method_class.name
        if method_class.schema:
            method_args = str(method_class.schema)
        else:
            method_args = inspect.getargs(method_class.run.im_func.func_code).args
            method_args.remove('self')
            method_args = ', '.join(method_args)

        docs = 'Name: {}\nArgs: {}\nDocs: {}\nReturn: {}'.format(
            method_name, method_args, method_docs,
            str(method_class.return_schema)
        )

        return docs

    def jsonrpc_list_methods(self):
        methods = []
        methods.extend(self.heisen_project.methods)

        if self.main_project:
            methods.extend(self.main_project.methods)

        methods = sorted(methods)

        return methods

    def jsonrpc_reload(self, path):
        if not settings.DEBUG:
            return

        module_path, _, module_name = path.replace('.py', '').rpartition('/')
        method = load_module(module_name, module_path)

        if settings.HEISEN_BASE_DIR in path:
            app_path = os.path.join(settings.HEISEN_BASE_DIR, 'apps')
            project = self.heisen_project
        elif hasattr(settings, 'BASE_DIR') and settings.BASE_DIR in path:
            app_path = os.path.join(settings.BASE_DIR, 'apps')
            project = self.main_project

        full_name = path.replace(app_path, '')\
                        .strip('/')\
                        .replace('/', '.')\
                        .replace('.py', '')\
                        .replace('.rpc', '')

        for subhandler in full_name.split('.')[:-1]:
            app = self.subHandlers[subhandler]

        app.set_method(full_name.split('.')[-1], method.RPC(full_name))

        message = 'Reloaded {}'.format(full_name)
        logger.service(message)
        print message

    def _ebRender(self, failure, id):
        if isinstance(failure.value, jsonrpclib.Fault):
            return failure.value

        message = failure.value.message
        code = self._map_exception(type(failure.value))
        logger.exception(failure.getTraceback())

        message = '{}|{}'.format(
            failure.type.__name__,
            failure.getErrorMessage()
        )

        return jsonrpclib.Fault(code, message)
