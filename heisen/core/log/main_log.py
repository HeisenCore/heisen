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

from heisen.core.utils.singleton import Singleton
from heisen.config import settings


class FormatterWithContextForException(logging.Formatter):
    def formatException(self, exc_info):
        (_type, value, tback) = exc_info

        frame_locals = {}
        if inspect.getinnerframes(tback) and inspect.getinnerframes(tback)[-1]:
            frame_locals = inspect.getinnerframes(tback)[-1][0].f_locals

        frame_locals.pop('__builtins__', None)
        return pprint.pformat(frame_locals) + '\n' + ''.join(traceback.format_exception(_type, value, tback))


class FilterWithAbsoluteModuleName(logging.Filter):
    def filter(self, record):
        record.absoluteModuleName = record.pathname.replace('.py', '', 1)\
                                                   .replace(settings.HEISEN_BASE_DIR, '', 1)\
                                                   .replace('/', '.')\
                                                   .lstrip('.')

        return True


def getExceptionText():
    """
        create and return text of last exception
    """
    _type, value, tback = sys.exc_info()
    frame_locals = {}

    if inspect.getinnerframes(tback) and inspect.getinnerframes(tback)[-1]:
        frame_locals = inspect.getinnerframes(tback)[-1][0].f_locals

    for var in frame_locals.keys():
        if var.startswith('__'):
            frame_locals.pop(var)

    text = pprint.pformat(frame_locals)
    text += '\n'
    text += ''.join(traceback.format_exception(_type, value, tback))
    return text


@Singleton
class Logger(object):
    formats = {
        'basic': '%(asctime)s - %(message)s',
        'complete': '%(asctime)s - [%(levelname)s] %(absoluteModuleName)s.%(funcName)s:%(lineno)d - %(message)s'
    }

    def __init__(self):
        if not hasattr(settings, 'LOGGERS'):
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
            return super(Connection, self).__getattr__(name)

    def exception(self, message='', logger='error'):
        getattr(self, logger)(
            '{}\n{}'.format(str(message), getExceptionText())
        )

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
            print 'Could not log to specified location, using StreamHandler'
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
