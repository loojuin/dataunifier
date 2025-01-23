"""
Main API entrypoint for :code:`dataunifier`.
"""

import csv
import sys
import time

from dataunifier.cmdline.constants import INPUT_DIR_OPTION_STUB, FORCE_OPTION, OUTPUT_OPTION_STUB
from dataunifier.common.exceptions import ExceptionWithMessage, AbortException
from dataunifier.config import config
from dataunifier.cmdline import cmdline
from dataunifier.logging import logging
from dataunifier.logging.constants import LOG_FILE_PATH_OPTION_STUB
from dataunifier.parse import parse
from dataunifier.utils import display


def print_usage():
    """
    Print the usage syntax.
    """

    display.stdout(f"Usage: $ python {sys.argv[0]} [{FORCE_OPTION}] "
                   f"[{LOG_FILE_PATH_OPTION_STUB}<log file path>] "
                   f"[{INPUT_DIR_OPTION_STUB}<input directory path>] "
                   f"[{OUTPUT_OPTION_STUB}<output file path>] "
                   f"<path to playbook>")


def main(args):
    """
    Main function that contains the key execution steps.

    Will raise exceptions extending :code:`ExceptionWithMessage`
    if there is any error, or :code:`AbortException` if aborted.

    :param list[str] args: List of strings containing command line arguments.
    """

    command_line_ctxt = cmdline.get_context(args)
    config_ctxt = config.get_context(command_line_ctxt)
    output_file_path = config_ctxt.output_file_path
    start = time.time()
    with open(output_file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, config_ctxt.fields)
        writer.writeheader()
        parse.start(config_ctxt, writer)
    end = time.time()
    dur = end - start
    display.stdout("Done. Took %.2f seconds." % dur)


def entry(args):
    """
    Entry point for the :code:`dataunifier` application.

    Does not throw exceptions, but instead catches them
    and handles the pretty-printing, and returns a return code instead.
    Suitable for being called by another application.

    :param list[str] args: List of strings containing command line arguments.
    :return: 0 if the programme executed successfully, 1 otherwise.
    :rtype: int
    """

    log_file_path = logging.extract_log_file_path(args)
    logging.initialise(log_file_path)
    try:
        main(args)
        return 0
    except ExceptionWithMessage as e:
        display.stdout()
        display.error(str(e))
        print_usage()
        return 1
    except AbortException:
        display.stdout()
        display.stdout("ABORTED.")
        return 1
