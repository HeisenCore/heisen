import logging
import inspect

from heisen.config import settings


class ProjectName(logging.Filter):
    def filter(self, record):
        record.project = settings.APP_NAME
        return True


class ExceptionHandler(logging.Filter):
    def filter(self, record):
        if isinstance(record.exc_info, tuple) and len(record.exc_info) == 3:
            exception = record.exc_info[1]
            record.exception_type = exception.__class__.__name__
            record.exception_message = str(exception)

            traceback_list = record.exc_info[-1]
            while traceback_list.tb_next:
                traceback_list = traceback_list.tb_next

            traceback_obj = inspect.getframeinfo(traceback_list)

            record.exception_filenamee = traceback_obj.filename
            record.exception_function = traceback_obj.function
            record.exception_line = traceback_obj.lineno

        return True
