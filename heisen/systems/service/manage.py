from heisen.systems.service import apps
from heisen.systems.service import utils
from heisen.systems.service.supervisor import supervisor

from heisen.config import settings


def create_config():
    utils.check_user()
    utils.change_ownership()
    virtual_env = utils.find_virtualenv()

    configs = [
        apps.UnixHttp(), apps.InetHttp(), apps.Group(),
        apps.ZMQ(virtual_env), apps.Heisen(virtual_env)
    ]

    if settings.DEBUG:
        configs.append(apps.WatchDog(virtual_env))

    for app in configs:
        app.write_config()

    supervisor.reload_config()
