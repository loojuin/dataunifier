"""
Module that handles file inputs and outputs.
"""

import csv
import os
import re

import yaml

from dataunifier.common import constants as commonconstants

from dataunifier.common.exceptions import AbortException, NoSuchDirectoryException, NoSuchFileException, \
    NoFileMatchingRegexException, YamlParsingException
from dataunifier.utils import display


def get_file_names_by_regex(directory, regex):
    """
    Get the names of files in a directory that match a regular expression.

    :param str directory: The path of the directory to search in.
    :param str regex: The regular expression.
    :return: The list of matching file names.
    :rtype: list[str]
    :raises: NoFileMatchingRegexException if no file matching the regular expression could be found.
    """

    if not os.path.isdir(directory):
        raise NoSuchDirectoryException(directory)
    files = os.listdir(directory)
    matching = [file for file in files if re.fullmatch(regex, file)]
    if not matching:
        raise NoFileMatchingRegexException(directory, regex)
    return matching


def check_file_existence(filepath):
    """
    Check whether a file exists.

    :param str filepath: Path of the file.
    :raises: NoSuchFileException if the specified path does not exist, or if it exists but is not a file.
    """

    if not os.path.isfile(filepath):
        raise NoSuchFileException(filepath)


def check_dir_existence(dirpath):
    """
    Check whether a directory exists.

    :param str dirpath: Path of the directory.
    :raises: NoSuchDirectoryException if the specified path does not exist, or if it exists but is not a directory.
    """

    if not os.path.isdir(dirpath):
        raise NoSuchDirectoryException(dirpath)


def strip_trailing_sep(path):
    """
    Strip the trailing file path separator from a path.

    e.g., :code:`/path/to/directory/` becomes :code:`/path/to/directory`.

    :param str path: The path to strip.
    :return: The path, with trailing separator removed.
    :rtype: str
    """

    return path.rstrip(os.path.sep)


def check_file_existence_and_confirm_overwrite(file_path_list, force=False):
    """
    Check if a list of files exist, and if any of the files exists, trigger a prompt to ask the user if the file
    should be overwritten.

    :param list[str] file_path_list: The list of files to check.
    :param bool force: If set to True, do not prompt the user and just overwrite the files without asking.
    :raises: AbortException if the user aborts.
    """

    exists = []
    for file_path in file_path_list:
        if os.path.isfile(file_path):
            exists.append(file_path)
    if not exists:
        return
    if force:
        display.stdout('The "force" flag has been set. Forcefully overwriting the following files:')
        for file_path in exists:
            display.stdout("  %s" % file_path)
    else:
        display.stdout('You are about to overwrite the following files:')
        for file_path in exists:
            display.stdout("  %s" % file_path)
        response = input(
            "Enter 'overwrite' to continue and overwrite (or set the -f option to avoid this prompt): "
        )
        if not response == "overwrite":
            raise AbortException()


def read_yaml_file(file_path):
    """
    Parse a YAML file and produce a :code:`dict` representation of it.

    :param str file_path: The path to the YAML file.
    :return: The YAML content
    :rtype: dict | list | None
    :raises: YamlParsingException if the file is not valid YAML.
    """

    check_file_existence(file_path)
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YamlParsingException(e)


def read_text_file(file_path):
    """
    Parse a text file as a string.

    :param str file_path: The path to the file.
    :return: The content of the file.
    :rtype: str
    """

    check_file_existence(file_path)
    with open(file_path, "r") as f:
        return f.read()


def get_extension(file_path):
    """
    Get the extension of a file.

    E.g., if the input is ":code: `test.csv`", output will be ":code:`csv`".

    :param str file_path: The filepath to get the extension from.
    :return: The extension of the file.
    :rtype: str
    """

    return file_path.split(os.path.sep)[-1].split(".")[-1]


def count_rows(file_path):
    """
    Count the number of rows in a CSV file.

    :param str file_path: The path of the file.
    :return: The number of CSV rows in the file.
    :rtype: int
    """

    counter = 0
    with open(file_path, "r", encoding=commonconstants.DEFAULT_ENCODING) as f:
        reader = csv.DictReader(f)
        for _ in reader:
            counter += 1
    return counter
