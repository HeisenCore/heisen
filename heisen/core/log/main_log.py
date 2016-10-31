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


class Logger(object):
    def __init__(self):
        if not hasattr(settings, 'LOGGERS'):
            print('*** No loggers found ***')
            return

        for logger_name, logger_config in settings.LOGGERS.items():
            logger = self.setup(
                logger_name,
                logger_config['format'],
                logger_config['level'],
            )
            setattr(self, logger_name, partial(logger.info))

            getattr(self, logger_name)(
                '--- Starting {} Logs ---'.format(logger_name.capitalize())
            )

    def exception(self, message='', logger='error'):
        message, extra = exceptions.format()

        getattr(self, logger)(message, extra=extra)

    def _rpc_exception(self, exc_info, logger='error'):
        message, extra = exceptions.format(exc_info)

        getattr(self, logger)(message, extra=extra)

    def setup(self, logger_name, logger_format, logger_level):
        logger = logging.getLogger(logger_name)
        logger.disabled = False
        logger.setLevel(logger_level)

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

        formatter = logging.Formatter(
            settings.LOG_FORMATS.get(logger_format, 'basic'),
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        try:
            handler = logging.handlers.RotatingFileHandler(
                join(log_dir, logger_name + '.log'),
                mode='a',
                maxBytes=settings.LOG_MAX_BYTES,
                backupCount=settings.LOG_BACKUP_COUNT
            )
        except IOError:
            warnings.warn('Could not log to specified location, using StreamHandler')
            print '*********** Could not log to specified location, using StreamHandler ***********'
            handler = logging.StreamHandler()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        try:
            import graypy

            graylog_config = getattr(settings, 'GRAYLOG', {})
            handler = graypy.GELFHandler(**graylog_config)

            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except ImportError:
            warnings.warn('Could not find graypy')
        else:
            print 'Send logs data to ', graylog_config['host']

        logger.propagate = False
        logger.addFilter(filters.ProjectName())
        logger.addFilter(filters.AbsoluteModuleName())

        if logger_name == 'py.warnings':
            logging.captureWarnings(True)

        return logger
