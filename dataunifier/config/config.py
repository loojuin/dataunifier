"""
Module for parsing configuration files.
"""

import functools

from dataunifier.config import keys, taskrouter, whenrouter
from dataunifier.config.classes import ConfigContext, Fileset, InputFile, Sheet, TaskParsingContext, WhenParsingContext
from dataunifier.common.exceptions import ConfigException, NoSuchTaskException
from dataunifier.tasks.BlockTask import BlockTask
from dataunifier.utils import regex, confighelper, display


def __parse_sheet_dict(sheet_spec_ctxt):
    valid_keys = {keys.REGEX, keys.MANDATORY}
    confighelper.check_invalid_keys(sheet_spec_ctxt, valid_keys)
    regex_list_ctxt = confighelper.get_literal_list(sheet_spec_ctxt, keys.REGEX, True)
    regex_list = [ctxt.value for ctxt in regex_list_ctxt.value]
    mandatory_ctxt = confighelper.get_boolean(sheet_spec_ctxt, keys.MANDATORY, False)
    mandatory = mandatory_ctxt.value if mandatory_ctxt else True
    return Sheet(regex_list, mandatory)


def __parse_sheet_spec(sheet_spec_ctxt):
    if isinstance(sheet_spec_ctxt.value, str):
        equivalent_regex = regex.regexify(sheet_spec_ctxt.value)
        return Sheet([equivalent_regex], True)
    return __parse_sheet_dict(sheet_spec_ctxt)


def __parse_sheet_spec_list(sheet_spec_list_ctxt):
    sheet_spec_ctxt_list = sheet_spec_list_ctxt.value
    return [__parse_sheet_spec(sheet_spec_ctxt) for sheet_spec_ctxt in sheet_spec_ctxt_list]


def __parse_input_file_dict(input_file_dict_ctxt):
    valid_keys = {keys.NAME, keys.REGEX, keys.SHEETS}
    confighelper.check_invalid_keys(input_file_dict_ctxt, valid_keys)
    name_ctxt = confighelper.get_literal(input_file_dict_ctxt, keys.NAME, True)
    name = name_ctxt.value
    regex_list_ctxt = confighelper.get_literal_list(input_file_dict_ctxt, keys.REGEX, True)
    regex_list = [ctxt.value for ctxt in regex_list_ctxt.value]
    sheet_spec_list_ctxt = confighelper.get_list(input_file_dict_ctxt, keys.SHEETS, False)
    sheets = __parse_sheet_spec_list(sheet_spec_list_ctxt) if sheet_spec_list_ctxt else None
    return InputFile(name, regex_list, sheets)


def __parse_input_file_dict_list(input_files_dict_list_ctxt):
    input_files_dict_ctxt_list = input_files_dict_list_ctxt.value
    return [__parse_input_file_dict(input_files_dict_ctxt) for input_files_dict_ctxt in input_files_dict_ctxt_list]


def __get_task_type(task_dict_ctxt, name):
    task_dict = task_dict_ctxt.value
    task_type = [key for key in task_dict.keys() if key not in (keys.NAME, keys.WHEN)]
    if len(task_type) != 1:
        msg = 'Multiple task type keys found in task "%s": "%s" (File "%s")' % (
            name, '", "'.join(task_type), task_dict_ctxt.current_file
        )
        raise ConfigException(msg)
    return task_type[0]


def __get_when_parsing_context(task_dict_ctxt):
    when_ctxt = confighelper.get_dict(task_dict_ctxt, keys.WHEN, False)
    if when_ctxt is None:
        return None
    return WhenParsingContext(when_ctxt, when_ctxt.current_file, when_ctxt.key_path, 0)


def __get_block_task(name, when, task_dict_ctxt, previous_task):
    block_list_ctxt = confighelper.get_dict_list(task_dict_ctxt, BlockTask.get_task_type_string(), True)
    task_dict_ctxt_list = block_list_ctxt.value
    if not task_dict_ctxt_list:
        msg = 'A task block must contain tasks. (File "%s", task block "%s", key "%s")' % (
            task_dict_ctxt.current_file, name, task_dict_ctxt.key_path
        )
        raise ConfigException(msg)
    inner_previous_task = previous_task
    task_list = []
    for inner_task_dict_ctxt in task_dict_ctxt_list:
        task = __parse_task_dict(inner_task_dict_ctxt, inner_previous_task)
        if not task.is_conditional():
            msg = f'{task.get_task_type_string()} tasks cannot be put inside a task block, because ' \
                  f'they cannot be used with "when".' \
                  f'(File "{inner_task_dict_ctxt.current_file}", Task "{task.name}")'
            raise ConfigException(msg)
        task_list.append(task)
        inner_previous_task = task
    return BlockTask(name, when, task_list)


def __parse_task_dict(task_dict_ctxt, previous_task):
    name_ctxt = confighelper.get_literal(task_dict_ctxt, keys.NAME, True)
    name = name_ctxt.value
    when_parsing_ctxt = __get_when_parsing_context(task_dict_ctxt)
    when = whenrouter.get_when(when_parsing_ctxt) if when_parsing_ctxt else None
    task_type = __get_task_type(task_dict_ctxt, name)
    if task_type == BlockTask.get_task_type_string():
        return __get_block_task(name, when, task_dict_ctxt, previous_task)
    inner_task_dict_ctxt = confighelper.get_dict(task_dict_ctxt, task_type, True)
    task_parsing_ctxt = TaskParsingContext(inner_task_dict_ctxt, name, task_type, when, previous_task)
    try:
        return taskrouter.get_task(task_parsing_ctxt)
    except NoSuchTaskException as e:
        msg = 'Unrecognized task type declared at key "%s": "%s" (File "%s")' % (
            task_dict_ctxt.key_path, e.task_type, task_dict_ctxt.current_file
        )
        raise ConfigException(msg)


def __parse_task_dict_list(task_dict_list_ctxt):
    output = []
    task_dict_ctxt_list = task_dict_list_ctxt.value
    previous_task = None
    for task_dict_ctxt in task_dict_ctxt_list:
        task = __parse_task_dict(task_dict_ctxt, previous_task)
        previous_task = task
        output.append(task)
    return output


def __parse_fileset_dict(fileset_dict_ctxt):
    valid_keys = {keys.NAME, keys.INPUT_FILES, keys.TASKS}
    confighelper.check_invalid_keys(fileset_dict_ctxt, valid_keys)
    name_ctxt = confighelper.get_literal(fileset_dict_ctxt, keys.NAME, True)
    name = name_ctxt.value
    input_files_dict_list_ctxt = confighelper.get_dict_list(fileset_dict_ctxt, keys.INPUT_FILES, False)
    input_files = __parse_input_file_dict_list(input_files_dict_list_ctxt) if input_files_dict_list_ctxt else None
    task_dict_list_ctxt = confighelper.get_dict_list(fileset_dict_ctxt, keys.TASKS, True)
    tasks = __parse_task_dict_list(task_dict_list_ctxt)
    if not tasks:
        msg = 'Task list for fileset "%s" is empty. You must specify at least one task. (File "%s")' % (
            name, fileset_dict_ctxt.current_file
        )
        raise ConfigException(msg)
    fields = tasks[-1].get_resulting_fields()
    return Fileset(name, fields, input_files, tasks)


def __parse_fileset_dict_list(fileset_dict_list_ctxt):
    fileset_dict_ctxt_list = fileset_dict_list_ctxt.value
    return [__parse_fileset_dict(fileset_dict_ctxt) for fileset_dict_ctxt in fileset_dict_ctxt_list]


def get_fields(filesets):
    """
    Get the fields that should be written into the output file.

    Checks that all FileSets result in the same list of fields,
    and raises :code:`ConfigException` if this is not the case.

    :param list[Fileset] filesets: Collection of FileSets.
    :return: List of fields.
    :rtype: list[str]
    :raises: ConfigException if the Filesets do not all produce the same list of fields.
    """

    fields = [fileset.fields for fileset in filesets]
    resulting_fields = functools.reduce(lambda x, y: y if x == y else None, fields)
    if not resulting_fields:
        msg = "Resulting fields for filesets do not match.\n%s" % (
            "\n".join(['Fields for fileset "%s": ["%s"]' % (fs.name, '", "'.join(fs.fields)) for fs in filesets])
        )
        raise ConfigException(msg)
    return resulting_fields


def __parse_config_dict(config_dict_ctxt):
    valid_keys = {keys.FILESETS}
    confighelper.check_invalid_keys(config_dict_ctxt, valid_keys)
    fileset_dict_list_ctxt = confighelper.get_dict_list(config_dict_ctxt, keys.FILESETS, True)
    filesets = __parse_fileset_dict_list(fileset_dict_list_ctxt)
    fields = get_fields(filesets)
    return ConfigContext(config_dict_ctxt.parent, fields, filesets)


def get_context(command_line_ctxt):
    """
    Get the :code:`ConfigContext` object that encapsulates the information specified in the command line arguments
    and the configuration file.

    :param CommandLineContext command_line_ctxt: The underlying context object containing command line arguments.
    :return: The context object that includes configuration information.
    :rtype: ConfigContext
    """
    display.stdout('Using configuration file "%s".' % command_line_ctxt.config_file_path)
    config_dict_ctxt = confighelper.parse_config_file(command_line_ctxt)
    config_ctxt = __parse_config_dict(config_dict_ctxt)
    return config_ctxt
