"""
Module containing logic to produce the correct When object from the configuration.
"""

from dataunifier.common.exceptions import ConfigException
from dataunifier.config import constants
from dataunifier.utils import confighelper
from dataunifier.when import ALL_WHEN_CLASSES, And, Or, Not

K_AND = "and"
K_OR = "or"
K_NOT = "not"


def __check_depth(when_parsing_ctxt):
    if when_parsing_ctxt.depth > constants.MAX_WHEN_DEPTH:
        msg = '"when" object at "%s" goes too deep (possibly due to infinite recursion). (File "%s")' % (
            when_parsing_ctxt.root_key_path, when_parsing_ctxt.root_file
        )
        raise ConfigException(msg)


def __get_and(when_parsing_ctxt):
    when_ctxt_list = confighelper.get_dict_list(when_parsing_ctxt, K_AND, True).value
    when_parsing_ctxt_list = [
        when_parsing_ctxt.next_depth(when_ctxt) for when_ctxt in when_ctxt_list
    ]
    when_objects = [get_when(when_parsing_ctxt) for when_parsing_ctxt in when_parsing_ctxt_list]
    return And(when_objects)


def __get_or(when_parsing_ctxt):
    when_ctxt_list = confighelper.get_dict_list(when_parsing_ctxt, K_OR, True).value
    when_parsing_ctxt_list = [
        when_parsing_ctxt.next_depth(when_ctxt) for when_ctxt in when_ctxt_list
    ]
    when_objects = [get_when(when_parsing_ctxt) for when_parsing_ctxt in when_parsing_ctxt_list]
    return Or(when_objects)


def __get_not(when_parsing_ctxt):
    when_ctxt = confighelper.get_dict(when_parsing_ctxt, K_NOT, True)
    next_when_parsing_ctxt = when_parsing_ctxt.next_depth(when_ctxt)
    next_when = get_when(next_when_parsing_ctxt)
    return Not(next_when)


def get_when(when_parsing_ctxt):
    """
    Get the right When object corresponding to the configuration block.

    :param WhenParsingContext when_parsing_ctxt: The context object for the "when" configuration block.
    :return: The "When" object.
    :rtype: AbstractWhen
    """

    __check_depth(when_parsing_ctxt)
    if when_parsing_ctxt.value.keys() == {K_AND}:
        return __get_and(when_parsing_ctxt)
    if when_parsing_ctxt.value.keys() == {K_OR}:
        return __get_or(when_parsing_ctxt)
    if when_parsing_ctxt.value.keys() == {K_NOT}:
        return __get_not(when_parsing_ctxt)
    for cls in ALL_WHEN_CLASSES:
        if when_parsing_ctxt.value.keys() == cls.get_key_set():
            return cls.create_from_config(when_parsing_ctxt)
    raise ConfigException('Could not interpret the "when" object at "%s". (File "%s")' % (
        when_parsing_ctxt.key_path, when_parsing_ctxt.current_file
    ))
