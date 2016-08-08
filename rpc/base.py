import abc
import datetime
import time

from twisted.internet import reactor
from twisted.internet.threads import deferToThreadPool
from cerberus import Validator
from cerberus import errors

from config.settings import APP_NAME
from config.settings import DEBUG

from core.log import logger
# from core.db import cursor_local
from core.threading_pool.core_thread import get_twisted_pool as pool


class PluginBase(object):
    __metaclass__ = abc.ABCMeta
    write_activity = True
    async = True
    schema = {}

    @abc.abstractmethod
    def run(self):
        pass

    def __init__(self):
        if self.write_activity:
            self.call.__func__.with_activity_log = True

    def call(self, *args, **kwargs):
        self.func_name = self.__full_name__
        self.username = kwargs.pop('rpc_username', None)
        self.src = kwargs.pop('rpc_address', None)
        time_start = time.time()

        if self.schema:
            validator = Validator(self.schema)
            valid = validator.validate(args)
            if not valid:
                raise AttributeError(validator.errors)

        if self.async:
            worker = deferToThreadPool(reactor, pool(), self.run, *args, **kwargs)

            if DEBUG:
                worker.addCallback(self._timeit, time_start, args, kwargs)

            if self.write_activity:
                worker.addCallback(self._write_activity_log, args, kwargs)

            return worker
        else:
            result = self.run(*args, **kwargs)

            if DEBUG:
                self._timeit(result, time_start, args, kwargs)

            if self.write_activity:
                self._write_activity_log(result, args, kwargs)

            return result


    def _timeit(self, result, ts, args, kwargs):
        te = time.time()
        start_time = datetime.datetime.fromtimestamp(int(ts)).strftime('%H:%M:%S')

        msg = "[{0}] - [{1}] - start: {2} - time: {3:2.1f}s - func: {4} - args: {5} - kwargs: {6}"
        msg = msg.format(self.src, self.username, start_time, te-ts, self.func_name, args, kwargs)
        logger.request(msg)

        return result

    def _write_activity_log(self, result, args, kwargs):
        doc = {
            'created_date':  datetime.datetime.now(),
            'username': self.username,
            'api_name': self.func_name,
            'address': self.src,
            'action': getattr(self, 'activity_name', self.func_name),
            'args': args[1:],
        }

        if hasattr(self, 'refine_activity_log'):
            doc = self.refine_activity_log(doc)

        # cursor_local.activity_log.insert(doc)

        return result
