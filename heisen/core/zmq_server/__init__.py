from multiprocessing import Pool
from multiprocessing import Process

from heisen.config import settings
from heisen.core.zmq_server.server import start_server


def start_zmq():
    if settings.START_ZMQ:
        p = Process(target=start_server)
        p.start()
