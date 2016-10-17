import re

from bson.regex import Regex
from bson import ObjectId
from cerberus import Validator as DefaultValidator
from cerberus import errors


class Validator(DefaultValidator):
    def _validate_info(self, isodd, field, value):
        """ {'type': 'string'} """
        pass

    def _validate_example(self, isodd, field, value):
        """ {'type': 'string'} """
        pass

    def _validate_require_if(self, schema_value, field, value):
        """ {'type': ['dict']} """

        require = True
        for document_key, document_value in schema_value.items():
            if self.document.get(document_key, None) != document_value:
                require = False

        if require and not value:
            self._error(
                field, "{} must not be empty when {} is {}".format(field, document_key, document_value)
            )

    def _validate_type_bsonregex(self, value):
        if isinstance(value, Regex):
            return True

    def _validate_type_objectid(self, value):
        if isinstance(value, ObjectId):
            return True

        if ObjectId.is_valid(value):
            return True

    def _validator_email(self, field, value):
        pattern = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        check_mail = re.match(pattern, value)
        if not check_mail:
            self._error(field, 'Not a valid email')

    # workaround for cerberus bug
    _validate_validator_email = _validator_email
