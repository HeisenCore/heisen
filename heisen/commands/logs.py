import os

from cliff.command import Command as CliffCommand

from heisen.core.log import logger
from heisen.config import settings


class Command(CliffCommand):
    def take_action(self, parsed_args):
        app_dirs = []
        base_dir = os.path.join(settings.LOG_DIR, settings.APP_NAME)

        for i in range(settings.INSTANCE_COUNT):
            app_dirs.append('{}{:02}/*.log'.format(base_dir, i + 1))

        os.system('tail -F {}'.format(' '.join(app_dirs)))
