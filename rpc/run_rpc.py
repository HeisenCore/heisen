import os
from threading import Thread
from twisted.internet import reactor
from twisted.web import server
from twisted.python import log
from twisted.cred.checkers import FilePasswordDB
from txjsonrpc.auth import wrapResource

from config.settings import CORE_PORT
from config.settings import CORE_ID
from config.settings import BASE_DIR
from config.settings import background_process_thread_pool as pool
from services.rpc_core.main_json_rpc import CoreServices


def runRPC():
    print 'Core Services running  \t\t\t\t\t\t[OK]'
    Thread(target=run_reactor).start()


def run_reactor():
    init = CoreServices()
    observer = log.PythonLoggingObserver()
    observer.start()
    dirname = os.path.dirname(__file__)
    checker = FilePasswordDB(BASE_DIR + "/config/passwd.db")
    realm_name = "Server Name: {}".format(CORE_ID)
    wrappedRoot = wrapResource(init, [checker], realmName=realm_name)
    reactor.listenTCP(CORE_PORT, server.Site(resource=wrappedRoot))
    reactor.suggestThreadPoolSize(pool)
    reactor.run(installSignalHandlers=False)
