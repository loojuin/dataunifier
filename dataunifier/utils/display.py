"""
This module provides functions for displaying things on the console.
"""

import sys

from dataunifier.logging import logging


class ProgressBar:
    """
    A class that, when instatiated, shows a progress bar on the console.
    """

    def __init__(self, total):
        """
        Create a :code:`ProgressBar`.

        :param int total: The "total" to be shown on the progress bar.
        """

        self.total = total
        self.progress = 0
        self.previous_bar_length = 0
        bar = " " * 101  # pylint: disable=blacklisted-name
        sys.stdout.write("[%s] 0/%d" % (bar, self.total))

    def increment(self, value=1):
        """
        Increment the counter by a value (default is 1).

        Note that this function does not necessarily cause the displayed progress bar to change.
        The progress bar will only become longer when the progress changes by one-hundredth of the total.

        :param int value: The amount to increment.
        """

        self.progress += value
        bar_length = int((self.progress/self.total) * 100) if self.total > 0 else 100
        if bar_length > self.previous_bar_length:
            space_length = 100 - bar_length
            bar = "=" * bar_length  # pylint: disable=blacklisted-name
            space = " " * space_length
            sys.stdout.write("\r[%s>%s] %d/%d" % (bar, space, self.progress, self.total))
        self.previous_bar_length = bar_length

    def close(self):
        """
        Close the progress bar.

        Causes the word :code:`DONE` to be printed at the end of the progress bar.
        """

        bar_length = int((self.progress/self.total) * 100) if self.total > 0 else 100
        space_length = 100 - bar_length
        bar = "=" * bar_length  # pylint: disable=blacklisted-name
        space = " " * space_length
        sys.stdout.write("\r[%s=%s] %d/%d DONE\n\n" % (bar, space, self.progress, self.total))


def stdout(msg=""):
    """
    Print a message to :code:`stdout`.

    :param str msg: The message to print.
    """

    print(msg)


def stderr(msg=""):
    """
    Print a message to :code:`stderr`.

    :param str msg: The message to print.
    """

    print(msg, file=sys.stderr)


def warn(msg):
    """
    Show a warning on the screen.

    :param str msg: The warning message.
    """

    logging.warn(msg)
    print("##### WARNING #####\n")
    print("  %s\n" % msg)
    print("###################")


def error(msg):
    """
    Print an error on the screen.

    :param str msg: The error message.
    """

    logging.error(msg)
    stderr()
    stderr("   EEEEEEEEE  RRRRRRRR   RRRRRRRR   OOOOOOOOO  RRRRRRRR ")
    stderr("   EEEEEEEEE  RRRRRRRRR  RRRRRRRRR  OOOOOOOOO  RRRRRRRRR")
    stderr("   EEE        RRR   RRR  RRR   RRR  OOO   OOO  RRR   RRR")
    stderr("   EEEEEEEEE  RRRRRRRRR  RRRRRRRRR  OOO   OOO  RRRRRRRRR")
    stderr("   EEEEEEEEE  RRRRRRR    RRRRRRR    OOO   OOO  RRRRRRR")
    stderr("   EEE        RRR  RRR   RRR  RRR   OOO   OOO  RRR  RRR")
    stderr("   EEEEEEEEE  RRR   RRR  RRR   RRR  OOOOOOOOO  RRR   RRR")
    stderr("   EEEEEEEEE  RRR   RRR  RRR   RRR  OOOOOOOOO  RRR   RRR")
    stderr()
    stderr(msg)
    stderr()
