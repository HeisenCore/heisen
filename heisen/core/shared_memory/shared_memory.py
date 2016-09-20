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

    def _process_message_shared_memory(self, message):
        if message['command'] == 'set_value':
            self.set_value(
                message['command'], message['key'], message['value'],
            )

        elif message['command'] == 'del_value':
            self.del_value(message['key'])

    def del_value(self, attr, key):
        var = getattr(self, attr)
        del var[key]

    @process
    def set_value(self, attr, key, value):
        var = getattr(self, attr)
        var[key] = value

    def get_value(self, attr, key):
        return getattr(self, attr)[key]

    def load_attrs(self, data):
        for doc in data:
            for k, v in doc.items():
                setattr(self, k, v)

    def retrive_attr(self, attr):
        return getattr(self, attr).copy()

    def retrive_attr_without_copy(self, attr):
        return getattr(self, attr)
