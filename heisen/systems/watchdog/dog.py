import os
import traceback
from multiprocessing import Process

from watchdog.observers import Observer
from watchdog import events

from heisen.core import rpc_call
from heisen.config import settings

from heisen.systems.service.supervisor import supervisor


class HeisenEventHandler(events.RegexMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        self.base_dir = kwargs.pop('base_dir', None)
        super(HeisenEventHandler, self).__init__(*args, **kwargs)

    def on_deleted(self, event):
        print 'Detected remove file event, restarting services'
        self.restart()

    def on_created(self, event):
        print 'Detected create file event, restarting services'
        self.restart()

    def on_modified(self, event):
        print 'Detected modify file event, restarting services'
        self.restart()

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

        if '#' in path:
            return

        try:
            rpc_call.self.reload(path)
        except Exception:
            traceback.print_exception()

    def restart(self):
        supervisor.restart()


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
        p = Process(name='heisen_monitor', target=monitor_heisen)
        p.start()

        p = Process(name='app_monitor', target=monitor_app)
        p.start()
