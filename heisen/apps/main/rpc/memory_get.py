from heisen.core.shared_memory import memory
from heisen.rpc.base import RPCBase


class RPC(RPCBase):
    documentation = """
        set attrs values into shared memory
    """

    def run(self, key):
        return memory.get(key)
