import os
from importlib import import_module
from heisen.config import settings_global


class Settings(object):
    def __init__(self):
        self.add_settings(settings_global)

        app_settings = import_module(os.environ.get('HEISEN_SETTINGS_MODULE'))

        self.add_settings(app_settings)

    def add_settings(self, module):
        for config in dir(module):
            if config == 'LOGGERS' and hasattr(self, 'LOGGERS'):
                self.LOGGERS.update(module.LOGGERS)
            elif config in os.environ:
                try:
                    setattr(self, config, int(os.environ[config]))
                except Exception as e:
                    setattr(self, config, os.environ[config])
                    print e
            elif config.isupper():
                setattr(self, config, getattr(module, config))


settings = Settings()
