"""
Module for regular expression-related tasks.
"""

import re


def regexify(string):
    """
    Turn a string into a regular expression that strictly matches itself.

    :param str string: The string to turn into a regular expression.
    :return: The regular expression.
    :rtype: str
    """

    return "^%s$" % re.escape(string)
