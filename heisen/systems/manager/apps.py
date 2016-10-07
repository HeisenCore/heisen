import os
from os.path import join, exists

from heisen.config import settings


class BaseConfig(object):
    user = os.environ['USER']
    startretries = 100
    stopasgroup = True
    autorestart = True
    autostart = True
    redirect_stderr = True

    def __init__(self, instance_number=1):
        self._instance_number = instance_number

        self.environment = self.get_environment()
        self.stdout_logfile = self.log_path()

    def configs(self):
        options = {}

        for option in dir(self):
            if not (option.startswith('_') or callable(getattr(self, option))):
                options[option] = getattr(self, option)

        return options

    def section_name(self):
        return 'program:{}'.format(self.name)

    def config_filename(self):
        return '{}.conf'.format(
            self.section_name().replace('program:', '')
        )

    def get_environment(self):
        environment = 'INSTANCE_NUMBER={}'.format(self._instance_number)

        path = None
        for method in [
                self._virtualenv_specified,
                self._virtualenv_wrapper,
                self._virtualenv_parent
        ]:
            path = method()
            if path:
                break

        if path:
            environment += ':PATH={}'.format(path)

        return environment

    def _is_virtualenv(self, path):
        virtualenv_dirs = ['bin', 'include', 'lib', 'local']
        is_virtualenv = all([
            exists(join(path, dir_name)) for dir_name in virtualenv_dirs
        ])

        if is_virtualenv:
            return join(path, 'bin')

    def _virtualenv_specified(self):
        if not getattr(settings, 'VIRTUALENV_DIR', None):
            return

        return self._is_virtualenv(settings.VIRTUALENV_DIR)

    def _virtualenv_wrapper(self):
        if not (
                os.environ.get('WORKON_HOME', None) and
                getattr(settings, 'WORKON_NAME', None)
        ):
            return

        virtualenv_dir = join(os.environ['WORKON_HOME'], settings.WORKON_NAME)
        return self._is_virtualenv(virtualenv_dir)

    def _virtualenv_parent(self):
        base_dir = getattr(settings, 'BASE_DIR', 'HEISEN_BASE_DIR')
        parent_dir = base_dir.rstrip('/').rpartition('/')[0]

        return self._is_virtualenv(parent_dir)


class ZMQ(BaseConfig):
    name = '{}_zmq'.format(settings.APP_NAME)
    directory = settings.HEISEN_BASE_DIR
    command = 'python systems/zmq/server.py'

    def log_path(self):
        return '{}{}_stdout.log'.format(settings.LOG_DIR, self.name)


class WatchDog(BaseConfig):
    name = '{}_watchdog'.format(settings.APP_NAME)
    directory = settings.HEISEN_BASE_DIR
    command = 'python systems/watchdog/dog.py'

    def log_path(self):
        return '{}{}_stdout.log'.format(settings.LOG_DIR, self.name)


class Heisen(BaseConfig):
    name = settings.APP_NAME
    directory = getattr(settings, 'BASE_DIR', settings.HEISEN_BASE_DIR)
    command = 'python {}.py run'.format(
        'manage' if hasattr(settings, 'BASE_DIR') else 'cli'
    )

    def __init__(self, instance_number=1):
        self.name = '{}{:02}'.format(self.name, instance_number)

        super(Heisen, self).__init__(instance_number)

    def log_path(self):
        log_dir = '{}{}{:02}/'.format(
            settings.LOG_DIR,
            settings.APP_NAME,
            self._instance_number
        )

        # TODO: move this to better place
        try:
            os.makedirs(log_dir, 0755)
        except Exception as e:
            pass

        return '{}stdout.log'.format(log_dir)
