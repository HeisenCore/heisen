# coding: utf-8
import os
import logging
from json import loads

import pytz


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOCAL_TZ = pytz.timezone('Asia/Tehran')

# Scheduler & CronJob
AP_THREADPOOL_EXECUTOR = 20
AP_PROCESSPOOL_EXECUTOR = 10
AP_COALESCE = False
AP_MAX_INSTANCES = 7

LOG_DIR = '/var/log/core/'
LOG_MAX_BYTES = 1000000
LOG_BACKUP_COUNT = 10
LOGGERS = {
    'error': {
        'format':'complete',
        'level': logging.INFO
    },
    'service': {
        'format':'basic',
        'level': logging.INFO
    },
    'db': {
        'format':'basic',
        'level': logging.INFO
    },
    'jobs': {
        'format':'complete',
        'level': logging.INFO
    },
    'request': {
        'format':'info',
        'level': logging.INFO
    },
    'debug': {
        'format':'complete',
        'level': logging.INFO
    },
    'apscheduler': {
        'format':'basic',
        'level': logging.DEBUG
    },
    'twisted': {
        'format':'basic',
        'level': logging.ERROR
    },
    'py.warnings': {
        'format':'basic',
        'level': logging.WARN
    },
}

installed_component = [
    "main",
    "jobs",
    "entry",
    "raspberry",
    "resource",
    "pa"
]


try:
    from settings_local import *
except ImportError:
    pass
