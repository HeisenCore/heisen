import urllib

from pymongo import MongoClient
from pymongo import ReadPreference
from pymongo import monitoring

from config.settings import DATABASES
from core.log import logger
from config import settings
from core.utils.singleton import Singleton


class CommandLogger(monitoring.CommandListener):
    def __init__(self, *args, **kwargs):
        self.log_query = kwargs.pop('log_query', True)
        self.log_query_data = kwargs.pop('log_query_data', False)
        self.log_results = kwargs.pop('log_results', False)

        super(CommandLogger, self).__init__(*args, **kwargs)

    def started(self, event):
        try:
            command = event.command.to_dict()
        except AttributeError:
            command = event.command

        collection = command.pop(event.command_name, '')

        command_string = ''
        if self.log_query_data:
            command_string = ', Command: {}'.format(command)

        string = '[Running] ID {} {}:{} {}.{}.{}{}'.format(
            event.operation_id,
            event.connection_id[0], event.connection_id[1],
            event.database_name, collection,
            event.command_name, command_string
        )
        logger.db(string)

    def succeeded(self, event):
        replay_string = ''
        if self.log_results:
            replay_string = ', Reply: {}'.format(event.reply)

        string = '[Success] ID {} {}:{} {}, Time: {}{}'.format(
            event.operation_id,
            event.connection_id[0], event.connection_id[1],
            event.command_name, event.duration_micros, replay_string
        )
        logger.db(string)

    def failed(self, event):
        string = '[Failed] ID {} {}:{} {}, Time: {}, Failure: {}'.format(
            event.operation_id,
            event.connection_id[0], event.connection_id[1],
            event.command_name, event.duration_micros, event.failure
        )
        logger.db(string)


class MongoConnection(object):
    __db = None
    def __init__(self, config_name):
        logger.db('Creating cursor instance for {} db'.format(config_name))
        self.db_settings = settings.DATABASES[config_name]

        self.get_connection()
        self.ensure_indexes()

    def get_connection(self):
        if self.db_settings.get('log_query', False):
            monitoring.register(CommandLogger(
                log_query_data=self.db_settings.pop('log_query_data', False),
                log_results=self.db_settings.pop('log_results', False)
            ))

        self.__db = MongoClient(
            self.connection_string,
            serverSelectionTimeoutMS=6000, maxPoolSize=None,
            read_preference=ReadPreference.NEAREST, connect=False
        )[self.db_settings['db']]

        return self.__db

    def get_cursor(self):
        return self.__db

    @property
    def connection_string(self):
        try:
            password = urllib.quote_plus(self.db_settings['password'])
            auth = '{0}:{1}@'.format(
                self.db_settings['user'], password
            )
        except KeyError:
            auth = ''

        try:
            address = self.db_settings['balancing']
        except KeyError:
            address = '{0}:{1}'.format(self.db_settings['host'], self.db_settings['port'])

        connection_string = 'mongodb://{}{}'.format(auth, address)

        return connection_string

    def ensure_indexes(self):
        pass


@Singleton
class MongoDatabases(object):
    def __init__(self):
        for database in DATABASES.keys():
            setattr(self, database, MongoConnection(database).get_cursor())
