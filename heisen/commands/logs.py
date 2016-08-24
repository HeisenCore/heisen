import os

from cliff.command import Command as CliffCommand

from heisen.core.log import logger
from heisen.config import settings


class Command(CliffCommand):
    def take_action(self, parsed_args):
        os.system('tail -f {}{}/*'.format(settings.LOG_DIR, settings.APP_NAME))
