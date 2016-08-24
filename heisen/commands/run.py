from cliff.command import Command as CliffCommand

from heisen.core.log import logger


class Command(CliffCommand):
    def take_action(self, parsed_args):
        try:
            from heisen.rpc.run import start_service
            start_service()
        except Exception as e:
            print 'Exiting with exception', e, 'Check logs for more info'
            logger.exception(e)
