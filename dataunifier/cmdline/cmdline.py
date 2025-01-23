"""
Module responsible for parsing command line arguments.
"""

import os

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.cmdline.constants import INPUT_DIR_OPTION_STUB, DEFAULT_INPUT_DIR, OUTPUT_OPTION_STUB, \
    DEFAULT_OUTPUT_FILE_PATH, FORCE_OPTION
from dataunifier.common.exceptions import SyntaxException, NoSuchDirectoryException, CommandLineException, \
    NoSuchFileException
from dataunifier.utils import fileio


def extract_options(args):
    """
    Split command line arguments into positional
    arguments and options, where options start with ":code:`--`".

    :param list[str] args: List of command line arguments.
    :return: A tuple containing a list of positional arguments, followed by a set of options
    :rtype: (list[str], set[str])
    """

    return [arg for arg in args if arg[0] != "-"], {arg for arg in args if arg[0] == "-"}


def get_input_directory(options):
    """
    Get the path to the input directory from the command line options, or the default if none is specified.

    :param set[str] | list[str] options: Collection of command line options.
    :return: The input directory path.
    :rtype: str
    """

    for option in options:
        if option.startswith(INPUT_DIR_OPTION_STUB):
            return option[len(INPUT_DIR_OPTION_STUB):]
    return DEFAULT_INPUT_DIR


def get_output_file(options):
    """
    Get the path to the output file from the command line options, or the default if none is specified.

    :param set[str] | list[str] options: Collection of command line options.
    :return: The output file path.
    :rtype: str
    """

    for option in options:
        if option.startswith(OUTPUT_OPTION_STUB):
            return option[len(OUTPUT_OPTION_STUB):]
    return DEFAULT_OUTPUT_FILE_PATH


def validate_input_dir(input_dir):
    """
    Validate the input directory path provided in the command line arguments.

    :param str input_dir: The input directory path.
    :raises: CommandLineException if input directory does not exist.
    """

    try:
        fileio.check_dir_existence(input_dir)
    except NoSuchDirectoryException:
        raise CommandLineException('Could not find input directory "%s".' % input_dir)


def validate_output_file_path(output_file_path, force):
    """
    Validate the output file path provided in the command line arguments.

    Responsible for prompting the user to confirm overwrite if the file already exists.

    :param str output_file_path: The output file path.
    :param bool force: Indicates whether to force an overwrite.
    :raises: CommandLineException if the output directory does not exist.
    :raises: AbortException if the user aborts.
    """

    output_file_dir_raw = os.path.dirname(output_file_path)
    output_file_dir = "." if output_file_dir_raw == "" else output_file_dir_raw
    try:
        fileio.check_dir_existence(output_file_dir)
    except NoSuchDirectoryException:
        raise CommandLineException('Directory for output file "%s" does not exist.' % output_file_dir)
    fileio.check_file_existence_and_confirm_overwrite([output_file_path], force)


def validate_config_file_path(config_file_path):
    """
    Validate the configuration file path provided in the command line options.

    :param str config_file_path: The configuration file path.
    :raises: CommandLineException if the specified configuration file does not exist.
    """

    try:
        fileio.check_file_existence(config_file_path)
    except NoSuchFileException:
        raise CommandLineException('Could not find configuration file "%s".' % config_file_path)


def get_context(sys_argv):
    """
    Encapsulate the command line arguments and options into a :code:`CommandLineContext` object.

    :param list[str] sys_argv: Iterable of command line arguments (usually a list)
    :return: The context object containing the command line arguments and options.
    :rtype: CommandLineContext
    """

    args, options = extract_options(sys_argv)
    if len(args) < 2:
        raise SyntaxException("Incorrect number of arguments.")
    input_dir = fileio.strip_trailing_sep(get_input_directory(options))
    output_file_path = get_output_file(options)
    force = FORCE_OPTION in options
    config_file_path = args[1]
    validate_input_dir(input_dir)
    validate_output_file_path(output_file_path, force)
    validate_config_file_path(config_file_path)
    return CommandLineContext(input_dir, output_file_path, force, config_file_path)
