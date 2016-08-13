import os

class Settings(object):
    def add_settings(self, module):
        for config in dir(module):
            if config == 'LOGGERS' and hasattr(self, 'LOGGERS'):
                self.LOGGERS.update(module.LOGGERS)
            elif config in os.environ:
                setattr(self, config, os.environ[config])
            else:
                setattr(self, config, getattr(module, config))

settings = Settings()
