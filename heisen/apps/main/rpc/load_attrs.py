from heisen.core.shared_memory import memory
from heisen.rpc.base import RPCBase


class RPC(RPCBase):
    documentation = """
        set attrs values into shared memory

        e.g:
        main.load_attrs(data) > bool

        Keyword arguments:
        data         -- Dumps of list of dict

        ACL:
            TODO:
    """

    def run(self, data):
        memory.load_attrs(data)

        return True
