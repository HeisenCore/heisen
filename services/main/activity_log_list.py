# python import
from bson.json_util import dumps

# Core Services import
from config.settings import activity_log
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class ActivityLogList:
    """
        ActivityLogList
    """
    __name__ = 'activity_log_list'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.activity_log_list'
    documentation = """
        Fetch your activity log

        e.g:
        main.activity_log_list() > dict

        Keyword arguments:

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        return dumps(activity_log)


ActivityLogList()
