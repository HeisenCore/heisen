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


def load_apps(app_dir):
    app_paths = []
    app_list = {}
    for dir_name, dirs, methods in os.walk(app_dir):
        if not dir_name.endswith('rpc'):
            continue

        full_app_name = dir_name.replace(app_dir, '').strip('/').replace('/', '.').rstrip('.rpc')
        logger.service('Adding App {}'.format(full_app_name))

        method_list = {}
        for method_name in methods:
            if method_name.startswith('__init__'):
                continue

            if not method_name.endswith('py'):  # only load py files, refactor later for pyc and so files
                continue

            file = None
            try:
                method_name = method_name.rpartition('.')[0]
                file, pathname, desc = imp.find_module(method_name, [dir_name])
                method = imp.load_module(method_name, file, pathname, desc)
                method_list[method_name] = method.RPC()

                method_full_name = '{}.{}'.format(full_app_name, method_name)

                logger.service('Added Plugin {}'.format(method_full_name))
                setattr(method_list[method_name], '__full_name__', method_full_name)
            except Exception as e:
                logger.exception(e)
                if file is not None:
                    file.close()

        app_paths.append(full_app_name)
        app_name = dir_name.split('/')[-2]

        app = App()
        app.set_methods(method_list)
        app_list[app_name] = app


    for path in app_paths:
        parts = path.split('.')

        if len(parts) > 1:
            parent = parts[-2]
            child = parts[-1]

            logger.service('Adding sub handler {} to {}'.format(child, parent))
            app_list[parent].set_sub_handler(child, app_list[child])

    return app_list


def load_all_apps():
    all_apps = {}

    for app_dir in settings.APP_DIRS:
        all_apps.update(load_apps(app_dir))

    if 'apps' in os.listdir(os.getcwd()):
        all_apps.update(load_apps(join(os.getcwd(), 'apps')))

    return all_apps


class Project(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.base_app_dir = join(project_dir, 'apps')
        self.app_dirs = []
        self.apps = {}

        self._load_apps()
        self._attach_sub_handlers()

    def get_apps(self):
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

            full_app_name = app_dir.replace(self.app_dir, '').strip('/').replace('/', '.')
            app_name = full_app_name.split('.')[-1]
            self.apps[full_app_name] = application

            logger.service('----- Adding App {} -----'.format(full_app_name))

            for method_name in self._get_method_list(rpc_dir):
                method_module = self._load_module(method_name, [rpc_dir])
                method_full_name = '{}.{}'.format(full_app_name, method_name)

                if method_module is None:
                    continue

                method_class = method_module.RPC(method_full_name)

                logger.service('Adding method {}'.format(method_full_name))
                application.add_method(method_name, method_class)

            logger.service('----- Finished Adding App {} -----'.format(full_app_name))

    def _attach_sub_handlers(self):
        for full_app_name, app_class in self.apps.items():
            parts = full_app_name.split('.')

            if len(parts) > 1:
                parent = parts[-2]
                child = parts[-1]

                logger.service('Adding sub handler {} to {}'.format(child, parent))
                self.apps[parent].set_sub_handler(child, self.apps[child])


    def get_config(self):
        pass

    def get_inits(self):
        pass
