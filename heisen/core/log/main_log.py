import os
import sys
from os.path import join
import logging
import logging.handlers
import warnings
from functools import partial

from heisen.config import settings
from heisen.core.log import filters
from heisen.core.log import exceptions
from heisen.core.log import external


class Logger(object):
    def __init__(self):
        if not hasattr(settings, 'LOGGERS'):
            print('*** No loggers found ***')
            return

        self.log_dir = self._log_dir()

        for logger_name, logger_config in settings.LOGGERS.items():
            formatter = logging.Formatter(
                settings.LOG_FORMATS.get(logger_config['format'], 'basic'),
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            logger = self.setup(
                logger_name,
                formatter,
                logger_config['level'],
            )
            setattr(self, logger_name, partial(logger.info))

            getattr(self, logger_name)(
                '--- Starting {} Logs ---'.format(logger_name.capitalize())
            )

            external.graylog(logger_name, logger, formatter)

    def _log_dir(self):
        log_dir = join(
            settings.LOG_DIR,
            '{}{:02}'.format(
                settings.APP_NAME,
                int(os.environ.get('INSTANCE_NUMBER', 1))
            )
        )

        try:
            os.makedirs(log_dir, 0755)
        except Exception:
            pass

        return log_dir

    def exception(self, message=None, logger='error'):

        message, extra = exceptions.format()
        getattr(self, logger)(message, extra=extra)

    def rpc_exception(self, exc_info, logger='error'):
        message, extra = exceptions.format(exc_info)

        getattr(self, logger)(message, extra=extra)

    def setup(self, logger_name, logger_format, logger_level):
        logger = logging.getLogger(logger_name)
        logger.disabled = False
        logger.setLevel(logger_level)

        try:
            handler = logging.handlers.RotatingFileHandler(
                join(self.log_dir, logger_name + '.log'),
                mode='a',
                maxBytes=settings.LOG_MAX_BYTES,
                backupCount=settings.LOG_BACKUP_COUNT
            )
        except IOError:
            warnings.warn('Could not log to specified location, using StreamHandler')
            print '*********** Could not log to specified location, using StreamHandler ***********'
            handler = logging.StreamHandler()

        handler.setFormatter(self.formatter)
        logger.addHandler(handler)

        logger.propagate = False
        logger.addFilter(filters.ProjectName())
        logger.addFilter(filters.AbsoluteModuleName())

        if logger_name == 'py.warnings':
            logging.captureWarnings(True)

        return logger
