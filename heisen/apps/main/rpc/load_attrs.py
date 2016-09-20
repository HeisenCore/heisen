from heisen.core.shared_memory import memory
from heisen.rpc.base import RPCBase


class RPC(RPCBase):
    documentation = """
        set attrs values into shared memory
    """

    schema = {
        'data': {
            'info': 'Dumps of list of dict'
        }
    }

    return_schema = {
        'types': [bool]
    }

    def run(self, data):
        memory.members = data

        return True
