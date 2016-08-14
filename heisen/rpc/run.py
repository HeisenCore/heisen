import os
from threading import Thread
from twisted.internet import reactor
from twisted.web import server
from twisted.python import log
from twisted.cred.checkers import FilePasswordDB
from txjsonrpc.auth import wrapResource

from heisen.config import settings
from heisen.rpc.main import CoreServices
from heisen.rpc.loader import load_projects


def start_service():
    print '{} Services Started'.format(settings.APP_NAME.capitalize())
    Thread(target=start_reactor).start()


def start_reactor():
    init = CoreServices()
    load_projects(init)
    observer = log.PythonLoggingObserver()
    observer.start()

    checker = FilePasswordDB(settings.HEISEN_BASE_DIR + "/config/passwd.db")
    realm_name = "Server Name: {}".format(settings.APP_NAME)
    wrappedRoot = wrapResource(init, [checker], realmName=realm_name)
    reactor.listenTCP(settings.RPC_PORT, server.Site(resource=wrappedRoot))
    reactor.suggestThreadPoolSize(settings.BACKGROUND_PROCESS_THREAD_POOL)

    reactor.run(installSignalHandlers=False)


    import base64
    auth = base64.encodestring(urllib.unquote('aliehsanmilad:Key1_s!3cr3t')).strip()
    auth = string.join(string.split(auth), "")
    extra_headers = [("Authorization", "Basic " + auth)]
