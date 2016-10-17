import os
import logging
import traceback
import datetime
from multiprocessing import Process

from watchdog.observers import Observer
from watchdog import events

from heisen.core import rpc_call
from heisen.config import settings

from heisen.systems.service.supervisor import supervisor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HeisenEventHandler(events.RegexMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        self.base_dir = kwargs.pop('base_dir', None)
        self.restart_delay = datetime.timedelta(seconds=10)
        self.last_restart = datetime.datetime.now()
        super(HeisenEventHandler, self).__init__(*args, **kwargs)

    def on_deleted(self, event):
        self.restart(event.src_path, 'deleted')

    def on_created(self, event):
        self.restart(event.src_path, 'created')

    def on_modified(self, event):
        self.restart(event.src_path, 'modified')

        # TODO: reload all instances of app
        # if 'rpc' in event.src_path:
        #     self.reload(event.src_path)
        # else:
        #     self.restart()

    def reload(self, path):
        if os.path.join(self.base_dir, 'apps') not in path:
            return

        if 'rpc' not in path:
            return

        try:
            rpc_call.self.reload(path)
        except Exception:
            traceback.print_exception()

    def restart(self, path, mode):
        if '#' in path:
            return

        if (datetime.datetime.now() - self.restart_delay) < self.last_restart:
            logger.info('Ignoring restart event')
            return

        logger.info('{} file {}, restarting services'.format(
            mode.capitalize(), path
        ))

        supervisor.restart()
        self.last_restart = datetime.datetime.now()


def monitor(directory):
    event_handler = HeisenEventHandler(
        regexes=['.*py$'],
        ignore_directories=True,
        case_sensitive=True,
        base_dir=directory,
    )

    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    observer.join()


def monitor_heisen():
    monitor(settings.HEISEN_BASE_DIR)


def monitor_app():
    if hasattr(settings, 'BASE_DIR'):
        monitor(settings.BASE_DIR)


if __name__ == '__main__':
    if settings.DEBUG:
        logger.info('Started monitoring directories')
        p = Process(name='heisen_monitor', target=monitor_heisen)
        p.start()

        p = Process(name='app_monitor', target=monitor_app)
        p.start()
