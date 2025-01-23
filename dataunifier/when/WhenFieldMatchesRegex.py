"""
Module for the :code:`WhenFieldMatchesRegex` class.
"""

import re

from dataunifier.common.exceptions import TransformationException
from dataunifier.utils import confighelper
from dataunifier.when.Abstract import AbstractRegularWhen

K_VALUE_OF_FIELD = "value_of_field"
K_MATCHES_REGEX = "matches_regex"


class WhenFieldMatchesRegex(AbstractRegularWhen):
    """
    Allows a task to proceed only if the value of a particular field matches a regular expression.
    """

    @classmethod
    def create_from_config(cls, when_parsing_context):
        field_name = confighelper.get_literal(when_parsing_context, K_VALUE_OF_FIELD, True).value
        regex_list_ctxt = confighelper.get_literal_list(when_parsing_context, K_MATCHES_REGEX, True)
        regex_list = [ctxt.value for ctxt in regex_list_ctxt.value]
        return WhenFieldMatchesRegex(field_name, regex_list)

    @classmethod
    def get_key_set(cls):
        return {K_VALUE_OF_FIELD, K_MATCHES_REGEX}

    def __init__(self, field_name, regex_list):
        """
        Create a :code:`WhenFieldMatchesRegex` object.

        :param str field_name: The name of the field to check.
        :param list[str] regex_list: A list of regular expressions to check against.
        """

        self.field_name = field_name
        self.regex_list = regex_list
        super(WhenFieldMatchesRegex, self).__init__()

    def __str__(self):
        return "WhenFieldMatchesRegex(%s matches %s)" % (
            self.field_name, self.regex_list
        )

    def __repr__(self):
        return str(self)

    def evaluate(self, row_ctxt):
        if self.field_name not in row_ctxt.rowdict:
            raise TransformationException('Could not find field "%s".' % self.field_name)
        value = row_ctxt.rowdict[self.field_name]
        return any([bool(re.fullmatch(regex, value)) for regex in self.regex_list])

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.field_name == other.field_name,
            self.regex_list == other.regex_list
        ])
