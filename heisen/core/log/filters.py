import logging

from heisen.config import settings


class ProjectName(logging.Filter):
    def filter(self, record):
        record.project = settings.APP_NAME
        return True


class AbsoluteModuleName(logging.Filter):
    def filter(self, record):
        record.absolute_module_name = record.pathname.replace('.py', '', 1).replace(settings.HEISEN_BASE_DIR, '', 1).replace('/', '.').lstrip('.')

        return True
