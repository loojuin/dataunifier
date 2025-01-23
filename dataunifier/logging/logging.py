"""
Module for handling logging.
"""

import logging

from dataunifier.logging import constants
from dataunifier.logging.constants import LOG_FILE_PATH_OPTION_STUB


def extract_log_file_path(args):
    """
    Extract the log file path from the command line arguments.

    The application will eventually write logs to this path.

    :param list[str] args: The command line arguments.
    :return: The log file path.
    :rtype: str
    """

    for arg in args:
        if arg.startswith(LOG_FILE_PATH_OPTION_STUB):
            return arg[len(LOG_FILE_PATH_OPTION_STUB):]
    return None


def initialise(error_log_path=None):
    """
    Initialise the logger.

    :param str error_log_path: The intended path of the error log.
    """

    logger = logging.getLogger()
    if logger.level != logging.DEBUG:
        logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        path = error_log_path if error_log_path else constants.DEFAULT_ERROR_LOG
        errorhandler = logging.FileHandler(path)
        errorhandler.setLevel(logging.WARN)
        errorformatter = logging.Formatter(constants.DEFAULT_ERROR_FORMAT)
        errorhandler.setFormatter(errorformatter)
        logger.addHandler(errorhandler)


def warn(msg):
    """
    Print a warning message to the log.

    :param str msg: The message.
    """

    logging.getLogger().warning(msg)


def error(msg):
    """
    Print an error message to the log.

    :param str msg: The message.
    """

    logging.getLogger().error(msg)
