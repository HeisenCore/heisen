import imp
import pprint
import os
from os.path import join, getsize
from collections import defaultdict

from txjsonrpc.web import jsonrpc

from core.log import logger
from config import settings


class App(jsonrpc.JSONRPC):
    def set_methods(self, methods):
        for method_name, method_class in methods.items():
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

            if not method_name.endswith('py'): # only load py files, refactor later for pyc and so files
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


    return all_apps
