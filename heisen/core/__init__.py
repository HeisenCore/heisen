from heisen.config import settings
from jsonrpclib.request import Connection


rpc_call = Connection(settings.RPC_SERVERS, 'heisen', settings.APP_NAME)
