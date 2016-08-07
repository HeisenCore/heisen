import imp
import os
import sys
import types

from core import logException
from core import toLog


class PluginLoader:
    def initPlugins(self, directory):
        """
            directory(text): directory path to search for plugins
            return all loaded module object
            call init function of all *.py files in "directory"
            they must register themselves somewhere
            ex. user plugins should user plugins.registerUserPlugin
        """
        py_files = self.__getPyFiles(directory)
        modules = {}
        modules.update(self.__loadArchivedModules(directory))
        modules.update(self.__loadModules(py_files, directory))
        self.__callInits(modules)
        return modules

    def __isClass(self, obj):
        return isinstance(obj, types.ClassType)

    def __callInits(self, modules):
        """
            call init function of all modules in "modules" dict
        """
        for obj in modules.itervalues():
            try:
                if hasattr(obj, 'init'):
                    obj.init()
            except:
                toLog('PluginLoader.__callInits', 'error')

    def __loadModules(self, py_list, directory):
        """
            load and import all files in "file_list" in path "directory"
            return a dic of loaded modules in format {module_name: module_obj}
        """
        modules = {}
        for file_name in py_list:
            file = None
            try:
                module_name = file_name[:-3]              # remove trailing.py
                file, pathname, desc = imp.find_module(module_name, [directory])
                modules[module_name] = imp.load_module(module_name, file, pathname, desc)
            except Exception as e:
                if file is not None:
                    file.close()
                logException('LoadModulesError: PluginLoader.__loadModules: ' '%s' % e)

        return modules

    def __getPyFiles(self, directory):
        """
            return list of all .py files in directory
        """
        return filter(
            lambda name: name.endswith('.py') or name.endswith('.so'),
            self.__getFilesList(directory)
        )

    def __getFilesList(self, directory):
        """
            return list of all files in "directory"
        """

        try:
            return os.listdir(directory)

        except OSError as e:
            toLog('PluginLoader.__getFilesList: %s' % e, 'error')
            return []

    def __loadArchivedModules(self, directory):
        """
            Look if there's any archived module available for this directory
        """
        # Start in here
        module = None

        if '' in sys.modules:
            module = sys.modules['']

        if module:

            if directory.endswith('rases'):
                return module.r

            elif directory.endswith('charge/attrs'):
                return module.c

        else:
            plugin = directory.split('/')[-1]
            module_name = 'services.plugins.{}.'.format(plugin)
            load_module = __import__(module_name, fromlist=["*"])
            module = {module_name: load_module}
            return module

        return {}
