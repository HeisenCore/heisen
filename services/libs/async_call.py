import abc
import datetime
import time

from functools import wraps
from twisted.internet import reactor
# from twisted.internet.threads import deferToThread
from twisted.internet.threads import deferToThreadPool
from txjsonrpc.web.jsonrpc import with_activity_log

from base_handler import exception_handler
from config.settings import CORE_NAME
from config.settings import DEBUG
from config.settings import activity_log
from config.settings import flight_activity_log
from core.log import logger
from core.db import cursor_local
from core.threading_pool.core_thread import get_twisted_pool as pool

from services.rpc_core.main_json_rpc import plugin_functions
from services.libs import plugin_handler


class PluginBase(object):
    __metaclass__ = abc.ABCMeta

    write_activity = True
    async = True

    def __init__(self):
        plugin_functions.append(cls.__full_name__)
        plugin = plugin_handler.initHandler()
        plugin.registerPlugin(cls())

        logger.service('Added Plugin {}'.format(cls.__full_name__))

    @abc.abstractmethod
    def run(self):
        pass

    def call(self, *args, **kwargs):
        self.run = exception_handler(self.run)
        self.run.with_activity_log = True

        args = list(args)
        username = args.pop(1)
        address = args.pop(1)
        args = tuple(args)

        ts = time.time()

        if self.async:
            worker = deferToThreadPool(reactor, pool(), cls, *args, **kwargs)
            worker.addErrback(to_log_error)

            if DEBUG:
                worker.addCallback(timeit, username, address, ts, args)

            worker.addCallback(write_activity_log, username, address, args)

            return worker
        else:
            result = self.run(*args, **kwargs)

            if DEBUG:
                timeit(result, username, address, ts, args)

            write_activity_log(result, username, address, args)

            return result


def timeit(result, username, address, ts, args):
    func_name = args[0].__class__.__full_name__
    te = time.time()
    start_time = datetime.datetime.fromtimestamp(int(ts)).strftime('%H:%M:%S')

    msg = "[{0}] - [{1}] - start: {2} - time: {3:2.1f}s - func: {4}({5})"
    msg = msg.format(address, username, start_time, te-ts, func_name, args[1:])
    logger.request(msg)

    return result


def to_log_error(failure):
    logger.error(str(failure))


def write_activity_log(result, username, address, args):
    func_name = args[0].__class__.__full_name__

    if hasattr(func_class, 'write_activity', False):
        doc = {
            'created_date':  datetime.datetime.now(),
            'username': username,
            'api_name': func_name,
            'address': address,
            'action': hasattr(func_class, 'activity_name', func_name),
            'args': args[1:],
        }

        if hasattr(func_class, 'refine_activity_log', None):
            doc = func_class.refine_activity_log(doc)

        cursor_local.activity_log.insert(doc)

    return result
