import abc
import inspect
import os
import pprint
import sys
from os.path import join
import traceback
import logging
import logging.handlers
import warnings
from functools import partial

from heisen.config import settings


class FormatterWithContextForException(logging.Formatter):
    def formatException(self, exc_info):
        return format_exception()


class FilterWithAbsoluteModuleName(logging.Filter):
    def filter(self, record):
        absoluteModuleName = record.pathname.replace('.py', '', 1).replace(settings.HEISEN_BASE_DIR, '', 1).replace('/', '.').lstrip('.')

        record.absoluteModuleName = absoluteModuleName

        return True


def format_exception(exc_info=None):
    """
        create and return text of last exception
    """

    if exc_info is None:
        _type, value, tback = sys.exc_info()
    else:
        _type, value, tback, traceback_text = exc_info

    frame_locals = {}

    if tback and inspect.getinnerframes(tback) and inspect.getinnerframes(tback)[-1]:
        frame_locals = inspect.getinnerframes(tback)[-1][0].f_locals

    for var in frame_locals.keys():
        if var.startswith('__'):
            frame_locals.pop(var)

    text = '{}\n'.format(pprint.pformat(frame_locals))

    if tback is not None:
        text += ''.join(traceback.format_exception(_type, value, tback))
    else:
        text += traceback_text

    return text


class Logger(object):
    formats = {
        'basic': '%(asctime)s - %(message)s',
        'complete': '%(asctime)s - [%(levelname)s] %(absoluteModuleName)s.%(funcName)s:%(lineno)d - %(message)s'
    }

    def __init__(self):
        if not hasattr(settings, 'LOGGERS'):
            print '*** No loggers found ***'
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

    def __getattr__(self, name):
        if not hasattr(settings, 'LOGGERS'):
            return partial(logging.info)
        else:
            return super(Logger, self).__getattr__(name)

    def exception(self, message='', logger='error'):
        getattr(self, logger)(
            '{}\n{}'.format(str(message), format_exception())
        )

    def _rpc_exception(self, exc_info, logger='error'):
        getattr(self, logger)(format_exception(exc_info))

    def setup(self, logger_name, logger_format, logger_level):
        logger = logging.getLogger(logger_name)
        logger.disabled = False
        logger.setLevel(logger_level)

        log_dir = join(settings.LOG_DIR, settings.APP_NAME)
        try:
            os.makedirs(log_dir, 0755)
        except Exception as e:
            pass

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

        formatter = FormatterWithContextForException(
            self.formats.get(logger_format, 'basic'),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.propagate = False
        filter = FilterWithAbsoluteModuleName()
        logger.addFilter(filter)

        return logger
