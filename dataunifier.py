"""
Command-line entry point for :code:`dataunifier`.
"""

import sys

import dataunifier.run as run


if __name__ == "__main__":
    RETCODE = run.entry(sys.argv)
    sys.exit(RETCODE)
