import imp
import pprint
import os
from os.path import join, getsize
from collections import defaultdict

from txjsonrpc.web import jsonrpc

from heisen.core.log import logger
from heisen.config import settings


class Application(jsonrpc.JSONRPC):
    def set_methods(self, methods):
        for method_name, method_class in methods.items():
            setattr(self, 'jsonrpc_{}'.format(method_name), method_class.call)

    def add_method(self, method_name, method_class):
        setattr(self, 'jsonrpc_{}'.format(method_name), method_class.call)

    def set_sub_handler(self, name, klass):
        self.putSubHandler(name, klass)


class Project(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.base_app_dir = join(project_dir, 'apps')
        self.app_dirs = []
        self.apps = {}
        self.methods = []

        if self.project_dir != settings.HEISEN_BASE_DIR:
            self._load_config()

        self._find_apps()
        self._load_apps()
        self._attach_sub_handlers()

    def _find_apps(self):
        for dir_name, dirs, methods in os.walk(self.base_app_dir):
            if 'rpc' not in dirs:
                continue

            self.app_dirs.append(dir_name)

    def _get_method_list(self, methods_path):
        methods = set()
        for method in os.listdir(methods_path):
            if method.startswith('__init__'):
                continue

            if not any([method.endswith(ext) for ext in ['.py', '.pyc', '.pyo', '.so']]):
                continue

            methods.add(method.rpartition('.')[0])

        return list(methods)

    def _load_module(self, module_name, module_path):
        file = None
        module = None
        try:
            file, pathname, desc = imp.find_module(module_name, [module_path])
            module = imp.load_module(module_name, file, pathname, desc)
        except Exception as e:
            logger.exception(e)
            if file is not None:
                file.close()

        return module

    def _load_apps(self):
        for app_dir in self.app_dirs:
            rpc_dir = join(app_dir, 'rpc')
            application = Application()

            full_app_name = app_dir.replace(self.base_app_dir, '').strip('/').replace('/', '.')
            app_name = full_app_name.split('.')[-1]
            self.apps[full_app_name] = application

            logger.service('----- Adding App {} -----'.format(full_app_name))

            for method_name in self._get_method_list(rpc_dir):
                method_module = self._load_module(method_name, rpc_dir)
                method_full_name = '{}.{}'.format(full_app_name, method_name)

                if method_module is None:
                    continue

                method_class = method_module.RPC(method_full_name)

                logger.service('Adding method {}'.format(method_full_name))
                application.add_method(method_name, method_class)
                self.methods.append(method_full_name)

            logger.service('----- Finished Adding App {} -----'.format(full_app_name))

    def _attach_sub_handlers(self):
        for full_app_name, app_class in self.apps.items():
            parts = full_app_name.rpartition('.')

            if parts[0] and parts[1]:
                parent = parts[0]
                child = parts[-1]

                logger.service('Adding sub handler {} to {}'.format(child, parent))
                self.apps[parent].set_sub_handler(child, self.apps[full_app_name])

    def _load_config(self):
        module = self._load_module('settings', join(self.project_dir, 'config'))

        if module is not None:
            settings.add_settings(module)

    def get_inits(self):
        pass


def load_projects(rpc_class):
    all_apps = {}
    all_apps.update(heisen_app.apps)
    all_apps.update(main_app.apps)

    for component, klass in all_apps.items():
        try:
            rpc_class.putSubHandler(component, klass)
        except Exception as e:
            logger.exception(e, 'service')
            logger.service("App {} failed to register".format(component))

    methods = []
    methods.extend(heisen_app.methods)
    methods.extend(main_app.methods)
    rpc_class.methods = sorted(methods)


heisen_app = Project(settings.HEISEN_BASE_DIR)
main_app = Project(os.getcwd())
