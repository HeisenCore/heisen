import os
from heisen.config import settings_global


class Settings(object):
    def __init__(self):
        self.add_settings(settings_global)

    def add_settings(self, module):
        for config in dir(module):
            if config == 'LOGGERS' and hasattr(self, 'LOGGERS'):
                self.LOGGERS.update(module.LOGGERS)
            elif config in os.environ:
                setattr(self, config, os.environ[config])
            elif config.isupper():
                setattr(self, config, getattr(module, config))


settings = Settings()
