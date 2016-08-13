from heisen.rpc.base import RPCBase

# from heisen.core.scheduler.scheduler import scheduler


class RPC(RPCBase):
    def run(self):
        return scheduler.print_jobs()
