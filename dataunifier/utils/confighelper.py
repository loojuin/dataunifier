"""
This module provides functions for traversing the YAML configuration file.

It provides the following key features:
 - Parsing of recursively imported text and YAML files, and integrating them into the object tree
 - Functions which expect key values to be specific types (literals, lists, or objects), and throw
   exceptions with helpful error messages should the types be unexpected.
"""

import os
import re

from dataunifier.config import constants
from dataunifier.config.classes import YamlPathContext
from dataunifier.common.exceptions import ConfigException, NoSuchFileException, YamlParsingException
from dataunifier.utils import fileio


def construct_key_path(key_path, next_key):
    """
    Construct the new key path when advancing deeper in the YAML structure.

    :param str key_path: The path of the current key.
    :param any next_key: The next key.
    :return: The new key path (basically a concatenation of the current key with the next key).
    :rtype: str
    """

    if key_path is None:
        return str(next_key)
    return "%s.%s" % (key_path, str(next_key))


def check_invalid_keys(context, valid_keys):
    """
    Assert that all keys inside a YAML object come from a set of valid keys.

    :param YamlPathContext context: The context object containing the YAML object.
    :param Set[str] valid_keys: The set of valid keys to check against.
    :raises: ConfigException if unrecognised keys are found.
    """

    invalid_keys = set(context.value.keys()) - valid_keys
    if invalid_keys:
        key_path = context.key_path
        if key_path:
            msg = 'Unrecognized configuration keys in object at "%s": "%s" (File "%s")' % (
                key_path, '", "'.join(invalid_keys), context.current_file
            )
        else:
            msg = 'Unrecognized configuration keys in file "%s": "%s"' % (
                context.current_file, '", "'.join(invalid_keys)
            )
        raise ConfigException(msg)


def parse_config_file(command_line_context):
    """
    Produce the :code:`YamlPathContext` containing the raw content of the config file.

    :param CommandLineContext command_line_context: The context object containing the config file path.
    :return: The context object containing the root YAML object in the config file (before expansion).
    :rtype: YamlPathContext
    :raises: ConfigException if the config file cannot be found or cannot be interpreted as YAML.
    """

    config_file_path = command_line_context.config_file_path
    try:
        return YamlPathContext(
            command_line_context, config_file_path, None, fileio.read_yaml_file(config_file_path)
        )
    except NoSuchFileException as e:
        raise ConfigException('Could not find configuration file "%s".' % e.file_path)
    except YamlParsingException as e:
        raise ConfigException('Could not interpret configuration file "%s". Details: %s' % (
            config_file_path, e.details
        ))


def parse_referenced_yaml_file(context, file_path):
    """
    Parse a referenced YAML file and return the corresponding context object.

    :param YamlPathContext context: The original context object containing the reference string.
    :param str file_path: The file path in the reference.
    :return: A context object containing the content of the file.
    :rtype: YamlPathContext
    :raises: YamlParsingException if the file could not be interpreted as YAML.
    :raises: NoSuchFileException if the file specified does not exist.
    """

    try:
        return YamlPathContext(
            context.parent, file_path, None, fileio.read_yaml_file(file_path)
        )
    except YamlParsingException as e:
        msg = 'Could not interpret YAML file "%s" (referenced in file "%s", key "%s"). Details: %s' % (
            file_path, context.current_file, context.key_path, e.details
        )
        raise ConfigException(msg)
    except NoSuchFileException:
        msg = 'Could not find YAML file "%s" (referenced in file "%s", key "%s")' % (
            file_path, context.current_file, context.key_path
        )
        raise ConfigException(msg)


def parse_referenced_text_file(context, file_path):
    """
    Parse a referenced text file and return the corresponding context object.

    :param YamlPathContext context: The original context object containing the reference string.
    :param str file_path: The file path in the reference.
    :return: A context object containing the content of the file.
    :rtype: YamlPathContext
    :raises: ConfigException if the specified text file does not exist.
    """

    try:
        return context.get_updated(context.key_path, fileio.read_text_file(file_path))
    except NoSuchFileException:
        msg = 'Could not find text file "%s" (referenced in file "%s", key "%s")' % (
            file_path, context.current_file, context.key_path
        )
        raise ConfigException(msg)


def __get_key(context, key, mandatory):
    if key not in context.value:
        if mandatory:
            key_path = context.key_path
            if key_path:
                msg = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                    key, key_path, context.current_file,
                )
            else:
                msg = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                    key, context.current_file
                )
            raise ConfigException(msg)
        return None
    return context.get_updated(construct_key_path(context.key_path, key), context.value[key])


def handle_placeholder_values_and_clean(context, filepath):
    """
    Replace filepath placeholder values with their actual values.

    For example, if the input directory is specified as :code:`/data1/test`,
    and the provided filepath is :code:`%INPUT_DIR%/input_dir`, the output
    would be :code:`/data1/test/input_dir`.

    Currently, only implemented placeholder value is :code:`%INPUT_DIR%`.

    :param CommandLineContext context: The underlying context.
    :param str filepath: The filepath containing the placeholder value.
    :return: The filepath with placeholder value substituted.
    :rtype: str
    """

    output = filepath.replace(constants.INPUT_DIR_PLACEHOLDER, context.input_dir)
    return os.path.relpath(output)


def __handle_recursive_parse(context):
    if isinstance(context.value, str):
        pattern = "{{ %s:(.+) }}" % constants.IMPORT_FILE_DIRECTIVE
        match = re.fullmatch(pattern, context.value)
        if match:
            file_path = handle_placeholder_values_and_clean(context, match.group(1).strip())
            if file_path[-5:] == ".yaml" or file_path[-4:] == ".yml":
                return parse_referenced_yaml_file(context, file_path)
            return parse_referenced_text_file(context, file_path)
    return context


def __get_key_with_recursive_parse(context, key, mandatory):
    next_context = __get_key(context, key, mandatory)
    if next_context is not None:
        next_context = __handle_recursive_parse(next_context)
    return next_context


def get_literal(context, key, mandatory):
    """
    Get the value of a key from a YAML object, where the value is supposed to be a literal (a single value).

    :param YamlPathContext context: The context object containing the YAML object.
    :param str key: The key to retrieve.
    :param bool mandatory: Indicates whether the key is mandatory, i.e., whether the programme should fail if the key
                           is missing.
    :return: The context object containing value of the key, or None if the key is missing and not mandatory.
    :rtype: YamlPathContext | None
    :raises: ConfigException if the value is a list or an object.
    """

    next_context = __get_key_with_recursive_parse(context, key, mandatory)
    if next_context is not None and (isinstance(next_context.value, (list, dict))):
        msg = 'Value of key "%s" is supposed to be a single value, not a list or an object. (File "%s")' % (
            next_context.key_path, next_context.current_file
        )
        raise ConfigException(msg)
    return next_context


def get_boolean(context, key, mandatory):
    """
    Get the value of a key from a YAML object, where the value is supposed to be a boolean.

    :param YamlPathContext context: The context object containing the YAML object.
    :param str key: The key to retrieve.
    :param bool mandatory: Indicates whether the key is mandatory, i.e., whether the programme should fail if the key
                           is missing.
    :return: The context object containing the value of the key, or None if the key is missing and not mandatory.
    :rtype: YamlPathContext | None
    :raises: ConfigException if the value is not a boolean.
    """

    next_context = get_literal(context, key, mandatory)
    if next_context is not None and not isinstance(next_context.value, bool):
        msg = 'Value of key "%s" is supposed to be a boolean. (File "%s")' % (
            next_context.key_path, next_context.current_file
        )
        raise ConfigException(msg)
    return next_context


def get_dict(context, key, mandatory):
    """
    Get the value of a key from a YAML object, where the value is supposed to be an object (dict).

    :param YamlPathContext context: The context object containing the YAML object.
    :param str key: The key to retrieve.
    :param bool mandatory: Indicates whether the key is mandatory, i.e., whether the programme should fail if the key
                           is missing.
    :return: The context object containing the value of the key, or None if the key is missing and not mandatory.
    :rtype: YamlPathContext | None
    :raises: ConfigException if the value is not an object (dict).
    """

    next_context = __get_key_with_recursive_parse(context, key, mandatory)
    if next_context is not None and next_context.value is None:
        next_context = next_context.get_updated(next_context.key_path, {})
    if next_context is not None and not isinstance(next_context.value, dict):
        msg = 'Value of key "%s" is supposed to be an object. (File "%s")' % (
            next_context.key_path, next_context.current_file
        )
        raise ConfigException(msg)
    return next_context


def get_list(context, key, mandatory):
    """
    Get the value of a key from a YAML object, where the value is supposed to be a list.

    :param YamlPathContext context: The context object containing the YAML object.
    :param str key: The key to retrieve.
    :param bool mandatory: Indicates whether the key is mandatory, i.e., whether the programme should fail if the key
                           is missing.
    :return: The context object containing the value of the key, or None if the key is missing and not mandatory.
    :rtype: YamlPathContext | None
    :raises: ConfigException if the value is not a list.
    """

    ls_context = __get_key_with_recursive_parse(context, key, mandatory)
    if ls_context is None:
        return None
    raw_list = ls_context.value if isinstance(ls_context.value, list) else [ls_context.value]
    ctxt_list = [
        ls_context.get_updated(construct_key_path(ls_context.key_path, i), raw_list[i]) for i in range(len(raw_list))
    ]
    expanded_ctxt_list = [__handle_recursive_parse(ctxt) for ctxt in ctxt_list]
    return ls_context.get_updated(ls_context.key_path, expanded_ctxt_list)


def get_literal_list(context, key, mandatory):
    """
    Get the value of a key from a YAML object, where the value is supposed to be a list of literals (not a list of
    objects).

    :param YamlPathContext context: The context object containing the YAML object.
    :param str key: The key to retrieve.
    :param bool mandatory: Indicates whether the key is mandatory, i.e., whether the programme should fail if the key
                           is missing.
    :return: The context object containing the value of the key, or None if the key is missing and not mandatory.
    :rtype: YamlPathContext | None
    :raises: ConfigException if the value is not a list of literals.
    """

    next_context = get_list(context, key, mandatory)
    if next_context is not None and not all([not isinstance(ctxt.value, dict) for ctxt in next_context.value]):
        msg = 'Value of key "%s" is supposed to be a list of single values, not a list of objects. ' \
              '(File "%s")' % (
                  next_context.key_path, next_context.current_file
              )
        raise ConfigException(msg)
    return next_context


def get_dict_list(context, key, mandatory):
    """
    Get the value of a key from a YAML object, where the value is supposed to be a list of objects (dicts).

    :param YamlPathContext context: The context object containing the YAML object.
    :param str key: The key to retrieve.
    :param bool mandatory: Indicates whether the key is mandatory, i.e., whether the programme should fail if the key
                           is missing.
    :return: The context object containing the value of the key, or None if the key is missing and not mandatory.
    :rtype: YamlPathContext | None
    :raises: ConfigException if the value is not a list of objects (dicts).
    """
    next_context = get_list(context, key, mandatory)
    if next_context is not None and not all([isinstance(ctxt.value, dict) for ctxt in next_context.value]):
        msg = 'Value of key "%s" is supposed to be a list of objects. (File "%s")' % (
            next_context.key_path, next_context.current_file
        )
        raise ConfigException(msg)
    return next_context
