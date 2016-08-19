from heisen.config import settings
from heisen.core.log import logger
from jsonrpclib.request import Connection


def get_rpc_connection():
    servers = {
        'self': [
            ('127.0.0.1', settings.RPC_PORT, 'aliehsanmilad', 'Key1_s!3cr3t')
        ],
    }

    servers.update(getattr(settings, 'RPC_SERVERS', {}))
    return Connection(servers, 'heisen', settings.APP_NAME)


rpc_call = get_rpc_connection()
# logger.debug(rpc_call.self.list_methods())
