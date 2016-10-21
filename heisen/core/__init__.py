from heisen.config import settings
from jsonrpclib.request import ConnectionPool


def get_rpc_connection():
    if settings.CREDENTIALS:
        username, passowrd = settings.CREDENTIALS[0]
    else:
        username = passowrd = None

    servers = {'self': []}
    for instance_number in range(settings.INSTANCE_COUNT):
        servers['self'].append((
            'localhost', settings.RPC_PORT + instance_number, username, passowrd
        ))

    servers.update(getattr(settings, 'RPC_SERVERS', {}))
    return ConnectionPool(servers, 'heisen', settings.APP_NAME)


rpc_call = get_rpc_connection()
