# python import
from pymongo import DESCENDING
from bson.json_util import loads
from bson.json_util import dumps

# Core Services import
from core.db import cursor_local
from services.plugins.entry.libs.func_tools import dict_sort
from services.plugins.entry.libs.func_tools import g_2_j
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class FetchActivityLogs:
    """
        FetchActivityLogs
    """
    __name__ = 'fetch_activity_log'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.fetch_activity_log'
    documentation = """
        Fetch your activity log

        e.g:
        main.fetch_activity_log(criteria, limit=100) > list

        Keyword arguments:
        criteria         -- Dumps of dict

        ACL:
            TODO:
    """

    @asynchronous
    def run(self, criteria, limit=100):
        criteria = loads(criteria)
        projection = {'_id': 0, 'flight_id': 0}
        sort = [('created_date', DESCENDING)]
        logs = cursor_local.activity_log.find(criteria, projection)
        logs = logs.sort(sort).limit(int(limit))

        new_list = []

        for doc in logs:

            if 'address' not in doc:
                doc['address'] = ''

            doc['created_date'] = g_2_j(doc.get('created_date', ''))
            new_list.append(dict_sort(doc))

        return dumps(new_list)


FetchActivityLogs()
