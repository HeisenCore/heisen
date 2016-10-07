from heisen.systems.manager import apps
from heisen.systems.manager import utils
from heisen.config import settings


def write_config():
    utils.check_user()
    utils.change_ownership()
    utils.write_config(settings.APP_NAME, apps.ZMQ())
    utils.write_config(settings.APP_NAME, apps.WatchDog())
    utils.write_config(settings.APP_NAME, apps.Heisen())


if __name__ == '__main__':
    write_config()
