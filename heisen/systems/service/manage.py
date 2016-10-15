from heisen.systems.manager import apps
from heisen.systems.manager import utils

from heapq.systems.service.supervisor import supervisor


def create_config():
    utils.check_user()
    utils.change_ownership()

    configs = [
        apps.UnixHttp(), apps.InetHttp(), apps.Group(),
        apps.ZMQ(), apps.WatchDog(), apps.Heisen()
    ]

    for app in configs:
        app.write_config()

    supervisor.reload_config()


if __name__ == '__main__':
    create_config()
