import xmlrpclib

from heisen.config import settings


class Supervisor(object):
    def __init__(self):
        self.server = xmlrpclib.Server('http://localhost:9900/RPC2')

    def restart(self):
        self.server.supervisor.stopProcessGroup(settings.APP_NAME)
        self.server.supervisor.startProcessGroup(settings.APP_NAME)

    def stop(self):
        self.server.supervisor.stopProcessGroup(settings.APP_NAME)

    def start(self):
        self.server.supervisor.startProcessGroup(settings.APP_NAME)

    def reload_config(self):
        self.server.supervisor.reloadConfig()


supervisor = Supervisor()
