from bson.json_util import dumps
from collections import defaultdict
from twisted.internet import reactor
from txjsonrpc.web import jsonrpc

from core.log import logger
from config.settings import installed_component
from core.manager.initialize_functions import initial_executer
from services.component.component_generator import generate_class_component


class CoreServices(jsonrpc.JSONRPC):
    global plugin_functions
    plugin_functions = []

    def __init__(self, user='', password=''):
        jsonrpc.JSONRPC.__init__(self)

        self.set_name_spacing()

        reactor.callInThread(initial_executer, )

    def set_name_spacing(self):
        for component in installed_component:
            try:
                klass = generate_class_component(component)
                self.putSubHandler(component, klass())

            except Exception as e:
                logger.exception(e)
                logger.error("Component {} Faild to register!".format(component))

    def jsonrpc_authinfo(self):
        return (self.request.getUser(), self.request.getPassword())

    def jsonrpc_methodHelp(self, method):
        method = self._getFunction(method)
        return dumps(getattr(method.im_class, 'documentation', ''))

    jsonrpc_methodHelp.signature = [['string', 'string']]

    def jsonrpc_listMethods(self):
        functions = []
        new_list = []
        dd = defaultdict(list)

        for item in plugin_functions:
            split_func_name = item.split('.')
            new_list.append({split_func_name[0]: [split_func_name[1]]})

        [dd[item.keys()[0]].append(item.values()[0][0]) for item in new_list]
        new_dict = dict(dd)
        todo = [(self, '')]

        while todo:
            obj, prefix = todo.pop(0)
            functions.extend([prefix + name for name in obj._listFunctions()])
            todo.extend([(obj.getSubHandler(name), prefix + name + obj.separator)
                         for name in obj.getSubHandlerPrefixes()])

        functions.sort()
        for item in new_dict:
            functions.append({item: new_dict[item]})

        return functions

    jsonrpc_listMethods.signature = [['array']]
