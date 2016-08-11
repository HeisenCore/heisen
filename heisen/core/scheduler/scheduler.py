import logging

from apscheduler import events
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.twisted import TwistedScheduler

from heisen.config import settings
from heisen.core.log import logger


executors = {
    'default': ThreadPoolExecutor(settings.AP_THREADPOOL_EXECUTOR),
    'processpool': ProcessPoolExecutor(settings.AP_PROCESSPOOL_EXECUTOR)
}

job_defaults = {
    'coalesce': settings.AP_COALESCE,
    'max_instances': settings.AP_MAX_INSTANCES
}

scheduler = TwistedScheduler(timezone=settings.LOCAL_TZ)
scheduler.add_jobstore(
    'mongodb',
    host=settings.DATABASES[settings.AP_DATABASE]['host'],
    port=settings.DATABASES[settings.AP_DATABASE]['port'],
    collection=settings.APP_NAME
)

scheduler.add_executor(
    ThreadPoolExecutor(settings.AP_THREADPOOL_EXECUTOR), 'default'
)

scheduler.add_executor(
    ProcessPoolExecutor(settings.AP_PROCESSPOOL_EXECUTOR), 'processpool'
)

scheduler.start()


def job_logger(event):
    if isinstance(event, events.JobExecutionEvent):
        logger.jobs('Job {}, code {}, run time {}, return value {}, exception {}'.format(
            event.job_id, event_code_translator(event.code),
            event.scheduled_run_time, event.retval, event.exception
        ))

    elif isinstance(event, events.JobSubmissionEvent) or isinstance(event, events.JobEvent):
        logger.jobs('Event {} for job {} happenend'.format(event_code_translator(event.code), event.job_id))

    else:
        logger.jobs('Event {} happenend'.format(event_code_translator(event.code)))


def event_code_translator(code):
    event_dict = {
        2 ** 0: 'EVENT_SCHEDULER_START',
        2 ** 1: 'EVENT_SCHEDULER_SHUTDOWN',
        2 ** 3: 'EVENT_SCHEDULER_PAUSED',
        2 ** 3: 'EVENT_SCHEDULER_RESUMED',
        2 ** 4: 'EVENT_EXECUTOR_ADDED',
        2 ** 5: 'EVENT_EXECUTOR_REMOVED',
        2 ** 6: 'EVENT_JOBSTORE_ADDED',
        2 ** 7: 'EVENT_JOBSTORE_REMOVED',
        2 ** 8: 'EVENT_ALL_JOBS_REMOVED',
        2 ** 9: 'EVENT_JOB_ADDED',
        2 ** 10: 'EVENT_JOB_REMOVED',
        2 ** 11: 'EVENT_JOB_MODIFIED',
        2 ** 12: 'EVENT_JOB_EXECUTED',
        2 ** 13: 'EVENT_JOB_ERROR',
        2 ** 14: 'EVENT_JOB_MISSED',
        2 ** 15: 'EVENT_JOB_SUBMITTED',
        2 ** 16: 'EVENT_JOB_MAX_INSTANCES',
    }

    return event_dict.get(code, None)

scheduler.add_listener(job_logger, events.EVENT_ALL)
