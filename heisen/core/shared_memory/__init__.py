from heisen.core.log import logger
from heisen.config import settings
from heisen.core.shared_memory.zmq_server import start_server
from heisen.core.shared_memory.shared_memory import SharedMemory
from multiprocessing import Pool
from multiprocessing import Process


if settings.START_ZMQ:
    p = Process(target=start_server)
    p.start()


memory = SharedMemory()
