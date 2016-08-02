# python import
from bson.json_util import dumps
from bson.json_util import loads

# Core Services import
from core.db import cursor_self
from services.libs.base_handler import DoseNotExist
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class GetFlightListFilter:
    """
        GetFlightListFilter
    """
    __name__ = 'get_flight_list_filter'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.get_flight_list_filter'
    documentation = """
        Getting filter by user key.

        e.g:
        api.get_flight_list_filter(username) > object

        Keyword arguments:
        username                -- String
        mode                    -- String  ( arr | dep )

        ACL:
            TODO:
    """

    @asynchronous
    def run(self, _user, mode):
        fetch = cursor_self.definitions.find_one(
            {
                '_type': 'flight_list_filter'
            }
        )

        if fetch:

            if fetch['value'].get(mode, {}):

                if fetch['value'][mode].get(_user, None):
                    val = fetch['value'][mode][_user]

                    return dumps(loads(val))

        return DoseNotExist("Dont have any filter!")


GetFlightListFilter()
