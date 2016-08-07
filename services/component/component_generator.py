from core.log import logger
from services.libs.base_rpc import BaseRPC
from txjsonrpc.web import jsonrpc

from config.settings import BASE_DIR
from services.libs import plugin_handler
from services.libs.plugin_loader import PluginLoader

import os
from os.path import join, getsize
from collections import defaultdict


def generate_class_component(app_dir):
    apps = {}
    all_files = defaultdict(list)

    for root, dirs, files in os.walk('.'):
        if root.endswith('rpc'):
            app_name = root.replace('/', '.')[7:]

            for plugin in files:
                if plugin.startswith('__init__'):
                    continue

                if plugin.split('.')[-1] in ['py', 'pyc', 'pyo', 'so']:
                    all_files[app_name].append(plugin)

    klass = type(app_name, (App, ), {})

    return apps


class App(jsonrpc.JSONRPC):
    def set_methods(self, methods):
        for method_name, method_class in methods.items():
            setattr(self, 'jsonrpc_{}'.format(method_name), method_class.call)

    def set_sub_handler(self, name, klass):
        self.putSubHandler(name, klass())


def reg():
    for component in installed_component:
        try:
            klass = generate_class_component(component)
            self.putSubHandler(component, klass())

        except Exception as e:
            logger.exception(e)
            logger.error("Component {} Faild to register!".format(component))
