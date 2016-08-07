import abc
import datetime
import time

from functools import wraps
from twisted.internet import reactor
# from twisted.internet.threads import deferToThread
from twisted.internet.threads import deferToThreadPool

# from base_handler import exception_handler
from config.settings import APP_NAME
from config.settings import DEBUG

from core.log import logger
# from core.db import cursor_local
from core.threading_pool.core_thread import get_twisted_pool as pool


class PluginBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.call.__func__.with_activity_log = True

    write_activity = True
    async = True

    @abc.abstractmethod
    def run(self):
        pass

    def call(self, *args, **kwargs):
        # self.run = exception_handler(self.run)

        self.func_name = self.__full_name__

        args = list(args)
        self.username = args.pop(0)
        self.src = args.pop(0)
        args = tuple(args)

        ts = time.time()

        if self.async:
            worker = deferToThreadPool(reactor, pool(), self.run, *args, **kwargs)
            worker.addErrback(self._to_log_error)

            if DEBUG:
                worker.addCallback(self._timeit, ts, args)

            worker.addCallback(self._write_activity_log, args)

            return worker
        else:
            result = self.run(*args, **kwargs)

            if DEBUG:
                self._timeit(result, ts, args)

            self._write_activity_log(result, args)

            return result


    def _timeit(self, result, ts, args):
        te = time.time()
        start_time = datetime.datetime.fromtimestamp(int(ts)).strftime('%H:%M:%S')

        msg = "[{0}] - [{1}] - start: {2} - time: {3:2.1f}s - func: {4}({5})"
        msg = msg.format(self.src, self.username, start_time, te-ts, self.func_name, args[1:])
        logger.request(msg)

        return result


    def _to_log_error(self, failure):
        logger.error(str(failure))


    def _write_activity_log(self, result, args):
        if self.write_activity:
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
