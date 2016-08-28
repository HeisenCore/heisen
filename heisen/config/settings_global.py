# coding: utf-8
import os
import logging
from json import loads

import pytz

HEISEN_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOCAL_TZ = pytz.timezone('Asia/Tehran')
RPC_PORT = 7089
APP_NAME = 'heisen'

DEBUG = True

BACKGROUND_PROCESS_THREAD_POOL = 120
MAIN_MIN_THREAD = 30
MAIN_MAX_THREAD = 80

AP_THREADPOOL_EXECUTOR = 20
AP_PROCESSPOOL_EXECUTOR = 10
AP_COALESCE = False
AP_MAX_INSTANCES = 7
AP_DATABASE = 'default'

ACTIVITY_LOG_DATABASE = 'default'

VALIDATOR_CLASS = 'heisen.core.validator.validator.Validator'

LOG_DIR = '/var/log/heisen/'
LOG_MAX_BYTES = 1000000
LOG_BACKUP_COUNT = 10
LOG_REQUEST = True
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
        'format':'basic',
        'level': logging.INFO
    },
    'debug': {
        'format':'complete',
        'level': logging.INFO
    },
    'zmq': {
        'format':'basic',
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

DATABASES = {
    'default': {
        'host': 'localhost',
        'port': 27017,
        'db': APP_NAME,
        'log_query': False,
        'log_query_data': False,
        'log_results': False,
    },
}

EMAIL_BACKEND = 'debug'
EMAIL_TEMPLATE_DIR = os.path.join(HEISEN_BASE_DIR, '/templates')

ZMQ = {
    'HOST': '127.0.0.1',
    'PUB': 5556,
    'REP': 5575
}

TOPICS = [
    'shared_memory',
    'controler',
    'signaling'
]
WAIT_MEMBER = 3
HEARTBEAT_TIME = 300

START_ZMQ = 1
PUB_SERVER_PORT = 5556
REP_SERVER_PORT = 5575
