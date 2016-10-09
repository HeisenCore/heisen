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
    numprocs = 1
    numprocs_start = 1

    def __init__(self):
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
        environment = 'INSTANCE_NUMBER="%(process_num)s"'

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
            environment += ',PATH="{}"'.format(path)

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
    process_name = '%(program_name)s%(process_num)02d'
    numprocs = settings.INSTANCE_COUNT
    command = 'python {}.py run'.format(
        'manage' if hasattr(settings, 'BASE_DIR') else 'cli'
    )

    def log_path(self):
        log_dir = '{}{}%(process_num)02d/'.format(
            settings.LOG_DIR,
            settings.APP_NAME
        )

        # TODO: move this to better place
        for i in range(settings.INSTANCE_COUNT):
            try:
                os.makedirs(log_dir % {'process_num': i + 1}, 0755)
            except Exception as e:
                pass

        return '{}stdout.log'.format(log_dir)
