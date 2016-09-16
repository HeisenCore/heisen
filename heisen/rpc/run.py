import sys
import io

from twisted.internet import reactor
from twisted.web import server
from twisted.logger import Logger, textFileLogObserver
from twisted.cred.checkers import FilePasswordDB
from txjsonrpc.auth import wrapResource

from heisen.config import settings
from heisen.rpc.main import Main
from heisen.rpc.auth import BasicCredChecker
from heisen.core.zmq_server import start_zmq
from heisen.core.watchdog import start_watchdog


def start_service():
    print '{} Services Started'.format(settings.APP_NAME.capitalize())
    sys.excepthook = excepthook
    start_zmq()
    start_watchdog()
    start_reactor()


def start_reactor():
    main = Main()

    # Logger(observer=textFileLogObserver(
    #     io.open("/var/log/heisen/test.log", "a")
    # ))

    if settings.CREDENTIALS:
        checker = BasicCredChecker(settings.CREDENTIALS)
        main = wrapResource(main, [checker], realmName=settings.APP_NAME)

    reactor.listenTCP(settings.RPC_PORT, server.Site(resource=main))
    reactor.suggestThreadPoolSize(settings.BACKGROUND_PROCESS_THREAD_POOL)

    reactor.run()


def excepthook(_type, value, traceback):
    import traceback
    print 'Printing exception via excepthook'
    traceback.print_exception(_type, value, traceback)
