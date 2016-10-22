import os
import signal

from cliff.command import Command as CliffCommand

from heisen.systems.service.supervisor import supervisor


class Command(CliffCommand):
    def take_action(self, parsed_args):
        procs = supervisor.get_proc_info()

        for proc in procs:
            if proc['statename'] == 'RUNNING':
                print('Printing stack trace for {}, check stdout'.format(proc['name']))
                os.kill(proc['pid'], signal.SIGWINCH)
