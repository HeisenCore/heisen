import abc
import os
import ConfigParser

from heisen.config import settings


class BaseConfig(object):
    __metaclass__ = abc.ABCMeta

    def configs(self):
        options = {}

        for option in dir(self):
            if not (option.startswith('_') or callable(getattr(self, option))):
                options[option] = getattr(self, option)

        return options

    def write_config(self):
        supervisor_config = '/etc/supervisor/conf.d/'
        config_parser = ConfigParser.RawConfigParser()

        config_parser.add_section(self._section_name)
        for option, value in sorted(self.configs().items()):
            config_parser.set(self._section_name, option, value)

        config_parser.remove_option(self._section_name, 'name')

        with open('{}{}.conf'.format(supervisor_config, self._filename), 'w') as configfile:
            supervisor_config,
            configfile.write('# Auto generated file, Don\'t edit.\n')
            config_parser.write(configfile)

        print('Created config file for {} in {}{}.conf'.format(
            self.name, supervisor_config, self._filename
        ))


class Application(BaseConfig):
    __metaclass__ = abc.ABCMeta

    user = os.environ.get('USER', None)
    startretries = 100
    stopasgroup = True
    autorestart = True
    autostart = True
    redirect_stderr = True
    numprocs = 1
    numprocs_start = 1
    environment = 'INSTANCE_NUMBER="%(process_num)s"'

    def __init__(self, virtualenv_dir):
        if virtualenv_dir:
            self.environment += ',PATH="{}"'.format(virtualenv_dir)
            print('Using {} as virtualenv directory'.format(virtualenv_dir))

        self.stdout_logfile = self.log_path()

        self._section_name = 'program:{}'.format(self.name)
        self._filename = self._section_name.replace('program:', '')


class UnixHttp(BaseConfig):
    name = 'unix_http_server'
    chmod = '0770'
    chown = '{}:{}'.format(os.environ.get('USER', None), os.environ.get('USER', None))

    def __init__(self):
        self._section_name = self.name
        self._filename = self.name


class InetHttp(BaseConfig):
    name = 'inet_http_server'
    port = '127.0.0.1:9900'

    def __init__(self):
        self._section_name = self.name
        self._filename = self.name


class Group(BaseConfig):
    name = settings.APP_NAME
    programs = settings.APP_NAME
    priority = 999

    def __init__(self):
        self._section_name = 'group:{}'.format(self.name)
        self._filename = 'group_{}'.format(self.name)


class ZMQ(Application):
    name = '{}_zmq'.format(settings.APP_NAME)
    directory = settings.HEISEN_BASE_DIR
    command = 'python systems/zmq/server.py'
    environment = (
        'INSTANCE_NUMBER="%(process_num)s",' +
        'PUB_SERVER_PORT="{}",' +
        'REP_SERVER_PORT="{}"'
    ).format(settings.ZMQ['PUB'], settings.ZMQ['REP'])

    def log_path(self):
        return '{}{}_stdout.log'.format(settings.LOG_DIR, self.name)


class WatchDog(Application):
    name = '{}_watchdog'.format(settings.APP_NAME)
    directory = settings.HEISEN_BASE_DIR
    command = 'python systems/watchdog/dog.py'

    def log_path(self):
        return '{}{}_stdout.log'.format(settings.LOG_DIR, self.name)


class Heisen(Application):
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
