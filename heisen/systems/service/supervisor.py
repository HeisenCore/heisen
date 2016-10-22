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

    def get_proc_info(self):
        procs = []
        for number in range(settings.INSTANCE_COUNT):
            procs.append(self.server.supervisor.getProcessInfo('{}:{}{:02d}'.format(
                settings.APP_NAME,
                settings.APP_NAME,
                number + 1
            )))

        return procs


supervisor = Supervisor()
