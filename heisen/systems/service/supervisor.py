import xmlrpclib


class Supervisor(object):
    def __init__(self):
        self.server = xmlrpclib.Server('http://localhost:9001/RPC2')

    def restart_heisen(self):
        self.server.supervisor.stopProcessGroup('heisen')
        self.server.supervisor.startProcessGroup('heisen')

    def reload_config(self):
        self.server.supervisor.reloadConfig()


supervisor = Supervisor()
