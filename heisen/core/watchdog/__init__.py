from multiprocessing import Pool
from multiprocessing import Process

from heisen.config import settings
from heisen.core.watchdog.dog import monitor_app, monitor_heisen


def start_watchdog():
    if settings.DEBUG:
        p = Process(name='heisen_monitor', target=monitor_heisen)
        p.start()

        p = Process(name='app_monitor', target=monitor_app)
        p.start()
