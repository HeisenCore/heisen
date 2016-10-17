import datetime
import time

from heisen.core.log import logger
from heisen.config import settings
from heisen.core.shared_memory.base import Base


def process(func):
    def execute(*args, **kwargs):
        if args[0].lock_time:
            now = datetime.datetime.now()
            lock = args[0].lock_time + datetime.timedelta(seconds=settings.WAIT_MEMBER)
            if now < lock:
                time.sleep(settings.WAIT_MEMBER)
                logger.zmq(
                    'Lock time: {0} | {1} | {2}'.format(
                        args[0].member_name,
                        args[1:],
                        kwargs
                    )
                )
        return func(*args, **kwargs)

    return execute


class SharedMemory(Base):
    topic = 'memory'

    def __init__(self):
        super(SharedMemory, self).__init__()

        for memory_name in settings.MEMORY_KEYS:
            setattr(self, memory_name, {})

    def __getitem__(self, key):
        for memory_name in settings.MEMORY_KEYS:
            return getattr(self, memory_name)
        else:
            raise KeyError()

    def _new_member(self):
        for memory_name in settings.MEMORY_KEYS:
            self._send_message('load_memory', memory_name, getattr(self, memory_name))

    def _memory_updated(self, memory_name):
        memory = getattr(self, memory_name)

        if not memory:
            return

        self._send_message('update', self.member_name, memory_name, memory)

    def update(self, member_name, memory_name, value):
        if member_name == self.member_name:
            return

        getattr(self, memory_name).update(**value)

    def load_memory(self, key, memory):
        if not memory:
            return

        getattr(self, key).update(**memory)

    # @process
    def set(self, memory_name, key, value):
        memory = getattr(self, memory_name)
        memory[key] = value

        self._memory_updated(memory_name)

    def get(self, memory_name):
        return getattr(self, memory_name)
