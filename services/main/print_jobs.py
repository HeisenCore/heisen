# python import
from bson.json_util import dumps

# Core Services import
from core.generals.scheduler import scheduler
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class PrintJobs:
    """
        PrintJobs
    """
    __name__ = 'print_jobs'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.print_jobs'
    documentation = """
        Print jobs.

        e.g:
        main.print_jobs() > list

        Keyword arguments:


        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        return dumps(scheduler.print_jobs())


PrintJobs()
