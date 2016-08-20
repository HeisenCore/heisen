from twisted.internet import reactor

from heisen.core.log import logger
from heisen.config import settings
from heisen.core.shared_memory.zmq_server import start_server
from heisen.core.shared_memory.shared_memory import SharedMemory


if settings.START_ZMQ:
    reactor.callInThread(start_server)


# memory = SharedMemory()
