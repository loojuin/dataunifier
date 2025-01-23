"""
Exception classes for use by this application.
"""

import os

import yaml

from dataunifier.common import constants


class ExceptionWithMessage(Exception):
    """
    Base class for any exception that carries a message.
    """

    def __init__(self, prefix: str, message: str):
        """
        Create an :code:`ExceptionWithMessage` object.

        :param prefix: The prefix (e.g., "PARSING ERROR")
        :param message: A message that describes the problem.
        """

        self.prefix = prefix
        self.message = message
        super(ExceptionWithMessage, self).__init__()

    def get_message_for_print(self) -> str:
        """
        Get the message that you can print onto the console.

        Concatenates the prefix and the message with a colon (:code:`:`)

        :return: The message for printing onto the console.
        """

        return "%s: %s" % (self.prefix, self.message)

    def __str__(self):
        return self.get_message_for_print()

    def __repr__(self):
        return str(self)


class NoSuchFieldException(ExceptionWithMessage):
    """
    Exception for situation where a field was expected but not found.
    """

    def __init__(self, message: str):
        super(NoSuchFieldException, self).__init__(constants.NO_SUCH_FIELD_EXCEPTION_PREFIX, message)


class AbortException(Exception):
    """
    Exception to effect a user abort.
    """


class SyntaxException(ExceptionWithMessage):
    """
    Exception for command line syntax errors.
    """

    def __init__(self, message: str):
        super(SyntaxException, self).__init__(constants.SYNTAX_EXCEPTION_PREFIX, message)


class CommandLineException(ExceptionWithMessage):
    """
    Exception for errors arising when parsing command line arguments.
    """

    def __init__(self, message: str):
        super(CommandLineException, self).__init__(constants.COMMAND_LINE_EXCEPTION_PREFIX, message)


class ConfigException(ExceptionWithMessage):
    """
    Exception for errors arising when parsing configuration file.
    """

    def __init__(self, message: str):
        super(ConfigException, self).__init__(constants.CONFIG_EXCEPTION_PREFIX, message)


class InputFileException(ExceptionWithMessage):
    """
    Exception for errors arising when trying to find or read input files.
    """

    def __init__(self, message: str):
        super(InputFileException, self).__init__(constants.INPUT_FILE_EXCEPTION_PREFIX, message)


class ParsingException(ExceptionWithMessage):
    """
    Exception for errors arising when trying to parse input files.
    """

    def __init__(self, message: str):
        super(ParsingException, self).__init__(constants.PARSING_EXCEPTION_PREFIX, message)


class NoSuchTaskException(Exception):
    """
    Exception for situation where a nonexistent task was invoked in a configuration file.

    For internal use. Not for displaying on console.
    """

    def __init__(self, task_type: str):
        """
        Create a :code:`NoSuchTaskException`.

        :param task_type: The task type string.
        """

        super(NoSuchTaskException, self).__init__()
        self.task_type = task_type


class NoSuchDirectoryException(Exception):
    """
    Exception for situation where a specified directory does not exist.

    For internal use. Not for displaying on console.
    """

    def __init__(self, directory_path: str):
        """
        Create a :code:`NoSuchDirectoryException`.

        :param directory_path: The path to the directory that is supposed to exist but does not.
        """

        super(NoSuchDirectoryException, self).__init__()
        self.directory_name = directory_path.split(os.path.sep)[-1]
        self.directory_path = directory_path


class NoSuchFileException(Exception):
    """
    Exception for situation where a specified file does not exist.

    For internal use. Not for displaying on console.
    """

    def __init__(self, file_path: str):
        """
        Create a :code:`NoSuchFileException`.

        :param file_path: The path to the file that is supposed to exist but does not.
        """

        super(NoSuchFileException, self).__init__()
        self.file_name = file_path.split(os.path.sep)[-1]
        self.file_path = file_path


class NoFileMatchingRegexException(Exception):
    """
    Exception for situation where the application cannot find any file whose name matches a regular expression.

    For internal use. Not for displaying on console.
    """

    def __init__(self, directory: str, regex: str):
        """
        Create a :code:`NoFileMatchingRegexException`.

        :param directory: The directory that the application was searching in.
        :param regex: The regular expression used.
        """

        super(NoFileMatchingRegexException, self).__init__()
        self.directory = directory
        self.regex = regex


class YamlParsingException(Exception):
    """
    Exception for YAML syntax errors in the configuration file.

    For internal use. Not for displaying on console.
    """

    def __init__(self, yaml_exception: yaml.YAMLError):
        """
        Create a :code:`YamlParsingException` from a previously thrown
        :code:`YAMLError`.

        :param yaml_exception: The original exception thrown by the YAML parsing library.
        """

        super(YamlParsingException, self).__init__()
        self.details = str(yaml_exception).replace("\r", "").replace("\n", ". ")


class TransformationException(Exception):
    """
    Exception for errors arising when attempting to perform transformations on input data.

    For internal usage. Not for displaying on console.
    """

    def __init__(self, message: str):
        self.message = message
        super(TransformationException, self).__init__()


class DiscardRecordException(Exception):
    """
    Exception for triggering a record to be discarded.
    """
