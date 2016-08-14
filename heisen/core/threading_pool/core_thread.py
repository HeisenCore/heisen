# python import
import random
from twisted.internet import reactor
from Queue import Queue
from threading import Thread
from twisted.python.threadpool import ThreadPool

from heisen.config import settings
from heisen.core.log import logger


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception, e:
                logger.error('Thread Error: %s' % e)
            self.tasks.task_done()


class ThreadPoolPython:
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kwargs):
        """Add a task to the queue"""

        key = random.randint(1000, 100000)
        msg = "Calling background process with id: {0} -- func: {1}"
        logger.jobs(msg.format(key, func.__name__))

        self.tasks.put((func, args, kwargs))

        logger.jobs("End of background process with id: {0}".format(key))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


def get_pool():
    pool = ThreadPoolPython(settings.BACKGROUND_PROCESS_THREAD_POOL)
    return pool


def get_twisted_pool():
    global pool

    try:
        return pool

    except:
        pool = ThreadPool(
            minthreads=settings.MAIN_MIN_THREAD,
            maxthreads=settings.MAIN_MAX_THREAD,
            name='core'
        )
        pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        return pool
