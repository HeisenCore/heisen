from cliff.command import Command as CliffCommand


from heisen.systems.service.supervisor import supervisor


class Command(CliffCommand):
    def take_action(self, parsed_args):
        supervisor.start()
