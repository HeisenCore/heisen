import os
from watchdog.observers import Observer
from watchdog import events

from heisen.core import rpc_call
from heisen.core.log import logger
from heisen.config import settings


class HeisenEventHandler(events.RegexMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        self.base_dir = kwargs.pop('base_dir', None)
        super(HeisenEventHandler, self).__init__(*args, **kwargs)

    def on_created(self, event):
        self.reload(event.src_path)

    def on_modified(self, event):
        self.reload(event.src_path)

    def reload(self, path):
        if os.path.join(self.base_dir, 'apps') not in path:
            return

        if 'rpc' not in path:
            return

        if '#' in path:
            return

        try:
            rpc_call.self.reload(path)
        except Exception as e:
            logger.exception(e)


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
