# python import


# Core Services import
from core import toLog
from services.rpc_core.main_json_rpc import plugin_functions
from services.libs import plugin_handler


def register(cls):
    def registerPlugin():
        """
           This module register every plugin that calls this method
        """
        toLog('Added Plugin {}'.format(cls.__full_name__), 'service')
        plugin_functions.append(cls.__full_name__)
        plugin = plugin_handler.initHandler()
        plugin.registerPlugin(cls())
    return registerPlugin
