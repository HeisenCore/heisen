import re

from bson.regex import Regex
from cerberus import Validator as DefaultValidator
from cerberus import errors


class Validator(DefaultValidator):
    def _validate_info(self, isodd, field, value):
        """ {'type': 'string'} """
        pass

    def _validate_example(self, isodd, field, value):
        """ {'type': 'string'} """
        pass

    def _validate_type_objectid(self, field, value):
        if re.match('[a-f0-9]{24}', str(value)):
            return True

    def _validate_type_bsonregex(self, field, value):
        if isinstance(value, Regex):
            return True

    def _validator_email(self, field, value):
        pattern = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        check_mail = re.match(pattern, value)
        if not check_mail:
            self._error(field, 'Not a valid email')

    # workaround for cerberus bug
    _validate_validator_email = _validator_email
