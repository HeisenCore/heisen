from heisen.core.log import logger
from heisen.config import settings
from heisen.core import rpc_call


def init():
    if settings.START_ZMQ:
        logger.debug('Running Main app init')
        logger.debug(rpc_call.self)
        s = rpc_call.self.list_methsods()
        logger.debug('Running Main app init')
        logger.debug(s)
        s = rpc_call.self.main.zmq_server()
        logger.debug('Running Main app init')
