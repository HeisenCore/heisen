import sys
import os
import io
import signal
import traceback
import socket

from twisted.internet import reactor
from twisted.web import server
from twisted.logger import Logger, textFileLogObserver
from txjsonrpc.auth import wrapResource

from heisen.config import settings
from heisen.core.log import logger
from heisen.rpc.main import Main
from heisen.rpc.auth import BasicCredChecker


def start_service():
    print('{} Services Started'.format(settings.APP_NAME.capitalize()))
    sys.excepthook = excepthook
    socket.setdefaulttimeout(settings.SOCKET_TIMEOUT)
    setup_signal_handlers()
    start_reactor()


def start_reactor():
    main = Main()

    # Logger(observer=textFileLogObserver(
    #     io.open("/var/log/heisen/test.log", "a")
    # ))

    if settings.CREDENTIALS:
        checker = BasicCredChecker(settings.CREDENTIALS)
        main = wrapResource(main, [checker], realmName=settings.APP_NAME)

    port = settings.RPC_PORT + int(os.environ.get('INSTANCE_NUMBER', 1)) - 1
    reactor.listenTCP(port, server.Site(resource=main))
    reactor.suggestThreadPoolSize(settings.BACKGROUND_PROCESS_THREAD_POOL)

    reactor.run()


def excepthook(_type, value, traceback):
    print('Printing exception via excepthook')
    traceback.print_exception(_type, value, traceback)


def setup_signal_handlers():
    if settings.DEBUG:
        logger.debug('Setting debug handlers')
        signal.signal(signal.SIGUSR1, embed)
        signal.signal(signal.SIGUSR2, trace)
        signal.signal(signal.SIGWINCH, print_trace)


def embed(sig, frame):
    try:
        from IPython import embed
        embed()
    except ImportError:
        import code
        code.interact(local=locals())


def trace(sig, frame):
    try:
        import ipdb as pdb
    except ImportError:
        import pdb

    pdb.set_trace()


def print_trace(sig, frame):
    traceback.print_stack()
