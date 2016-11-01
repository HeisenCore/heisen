import logging

from heisen.config import settings


class ExtraFields(logging.Filter):
    def filter(self, record):
        for key, value in getattr(settings, 'EXTERNAL_FIELDS', {}).items():
            setattr(record, key, value)

        return True


class AbsoluteModuleName(logging.Filter):
    def filter(self, record):
        record.absolute_module_name = record.pathname.replace('.py', '', 1).replace(settings.HEISEN_BASE_DIR, '', 1).replace('/', '.').lstrip('.')

        return True
