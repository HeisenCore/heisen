import re

from bson.regex import Regex
from cerberus import Validator as DefaultValidator
from cerberus import errors


class Validator(DefaultValidator):
    def _validate_isodd(self, isodd, field, value):
        pass

    def _validate_type_objectid(self, field, value):
        if not re.match('[a-f0-9]{24}', str(value)):
            self._error(field, errors.ERROR_BAD_TYPE.format('ObjectId'))

    def _validate_type_bsonregex(self, field, value):
        if not isinstance(value, Regex):
            self._error(field, errors.ERROR_BAD_TYPE.format('BsonRegex'))

    def _validate_type_email(self, field, value):
        if not (isinstance(value, str) or isinstance(value, unicode)):
            self._error(field, errors.ERROR_BAD_TYPE.format('String'))

        pattern = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        check_mail = re.match(pattern, value)
        if not check_mail:
            self._error(field, errors.ERROR_BAD_TYPE.format('Email'))
