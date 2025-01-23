"""
Classes for use in parsing configuration files.
"""

from dataunifier.cmdline.classes import CommandLineContext


class YamlPathContext(CommandLineContext):
    """
    Context class for encapsulating information about the current key in a YAML file being parsed.

    You should not be instantiating this class directly. Instead, utility methods have been provided in
    :code:`utils.confighelper` for navigating a YAML file.
    """

    def __init__(self, command_line_context, current_file, key_path, value):
        """
        Create a :code:`YamlPathContext` object.

        :param CommandLineContext command_line_context: The underlying command line context.
        :param str current_file: The path of the current YAML file being parsed.
        :param Optional[str] key_path: The path of the key currently being looked at. Should be a string comprised
                                       of all ancestor keys and the current key, concatenated using a period
                                       (e.g., "some.path.to.key"). Set to None if at the root of the file.
        :param Union[str, List, Dict] value: The value of the key.
        """

        super(YamlPathContext, self).__init__(
            command_line_context.input_dir,
            command_line_context.output_file_path,
            command_line_context.force,
            command_line_context.config_file_path
        )
        self.parent = command_line_context
        self.current_file = current_file
        self.key_path = key_path
        self.value = value

    def get_updated(self, next_key_path, next_value):
        """
        Get a new :code:`YamlPathContext` for another key, but for the same file.

        :param Optional[str] next_key_path: The path to the new key.
        :param Union[str, List, Dict] next_value: The value of the new key.
        :return: A new object updated with the new key and value.
        :rtype: YamlPathContext
        """

        return YamlPathContext(self.parent, self.current_file, next_key_path, next_value)

    def __str__(self):
        return "YamlPathContext(%s, %s, %s = %s)" % (self.parent, self.current_file, self.key_path, self.value)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.parent == other.parent,
            self.current_file == other.current_file,
            self.key_path == other.key_path,
            self.value == other.value
        ])


class WhenParsingContext(YamlPathContext):
    """
    Extension of the :code:`YamlPathContext` class for use when parsing a :code:`when` block.

    Main use of this class is to preserve information about the root of the :code:`when` block, since
    :code:`when` blocks have the potential to be infinitely recursive.
    """

    def __init__(self, yaml_path_context, root_file, root_key_path, depth):
        """
        Create a :code:`WhenParsingContext` object.

        :param YamlPathContext yaml_path_context: The context object for the current YAML key.
        :param str root_file: The path of the original file where the "when" block started.
        :param str root_key_path: The key path of the start of the "when" block.
        :param int depth: The level of nestedness of the when clause currently being parsed.
        """

        super(WhenParsingContext, self).__init__(
            yaml_path_context.parent,
            yaml_path_context.current_file,
            yaml_path_context.key_path,
            yaml_path_context.value
        )
        self.parent = yaml_path_context
        self.root_file = root_file
        self.root_key_path = root_key_path
        self.depth = depth

    def __str__(self):
        return "WhenParsingContext(%s, %s, %s, %s)" % (
            self.parent, self.root_file, self.root_key_path, self.depth
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.parent == other.parent,
            self.root_file == other.root_file,
            self.root_key_path == other.root_key_path,
            self.depth == other.depth
        ])

    def next_depth(self, yaml_path_context):
        """
        Create a new :code:`WhenParsingContext` for a new YAML key, but with incremented nestedness depth.

        :param YamlPathContext yaml_path_context: The new YAML path context object.
        :return: A new WhenParsingContext object for the new YAML path, with incremented depth.
        :rtype: WhenParsingContext
        """

        return WhenParsingContext(yaml_path_context, self.root_file, self.root_key_path, self.depth + 1)


class TaskParsingContext(YamlPathContext):
    """
    Extension to the :code:`YamlPathContext` class for use in parsing the inner portion of a task block.
    """

    def __init__(self,
                 yaml_path_context,
                 task_name: str,
                 task_type: str,
                 when,
                 previous_task):
        """
        Create a :code:`TaskParsingContext` object.

        :param YamlPathContext yaml_path_context: The YAML path context object containing the inner object in a task
                                                  block.
        :param str task_name: The name of the task.
        :param str task_type: The task type.
        :param AbstractWhen when: The "when" object for the task.
        :param AbstractTask previous_task: The previous task, or None if this is the first task.
        """

        super(TaskParsingContext, self).__init__(
            yaml_path_context.parent,
            yaml_path_context.current_file,
            yaml_path_context.key_path,
            yaml_path_context.value
        )
        self.parent = yaml_path_context
        self.task_name = task_name
        self.task_type = task_type
        self.when = when
        self.previous_task = previous_task

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.parent == other.parent,
            self.task_name == other.task_name,
            self.task_type == other.task_type,
            self.when == other.when,
            self.previous_task == other.previous_task
        ])


class Sheet:
    """
    Contains information about an Excel sheet to be parsed (not the actual data in the sheet).
    """

    def __init__(self, regex_list, mandatory):
        """
        Create a :code:`Sheet` object.

        :param list[str] regex_list: A list of regular expressions that identify the sheet name.
        :param bool mandatory: Indicates whether the sheet is mandatory - i.e., whether the application should fail
                               if the sheet cannot be found.
        """

        self.regex_list = regex_list
        self.mandatory = mandatory

    def __str__(self):
        return "Sheet(%s, %s)" % (self.regex_list, self.mandatory)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.regex_list == other.regex_list,
            self.mandatory == other.mandatory
        ])


class InputFile:
    """
    Contains information about a file to be parsed (not the actual data in the file).
    """

    def __init__(self, name, regex_list, sheets):
        """
        Create an :code:`InputFile` object.

        :param str name: A descriptive name to describe the input file (not the filename).
        :param list[str] regex_list: A list of regular expressions by which to recognise the file name.
        :param list[Sheet] | None sheets: The sheets in the file to be parsed, or None if there is no such concept
                                   (as with a CSV file).
        """

        self.name = name
        self.regex_list = regex_list
        self.sheets = sheets

    def __str__(self):
        return "InputFile(%s, %s, %s)" % (self.name, self.regex_list, self.sheets)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.regex_list == other.regex_list,
            self.sheets == other.sheets
        ])


class Fileset:
    """
    Contains information about a set of files to parse, and the tasks to apply to all of them.
    """

    def __init__(self, name, fields, input_files, tasks):
        """
        Create a :code:`Fileset` object.

        :param str name: A descriptive name for the set.
        :param list[str] fields: The resulting list of fields that should be outputted after all the tasks are complete.
        :param list[InputFile] input_files: The input files to be parsed.
        :param list[AbstractTask] tasks: The tasks to apply to the input files.
        """

        self.name = name
        self.fields = fields
        self.input_files = input_files
        self.tasks = tasks

    def __str__(self):
        return "Fileset(%s, %s, %s, %s)" % (self.name, self.fields, self.input_files, self.tasks)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.fields == other.fields,
            self.input_files == other.input_files,
            self.tasks == other.tasks
        ])


class ConfigContext(CommandLineContext):
    """
    Context object encapsulating the entities specified in the configuration file.

    Includes command line argument information as well.
    """

    def __init__(self, command_line_context, fields, filesets):
        """
        Create a :code:`ConfigContext` object.

        :param CommandLineContext command_line_context: The underlying command line context object.
        :param list[str] fields: The fields that the output file should have.
        :param list[Fileset] filesets: The sets of files to be parsed and their corresponding tasks.
        """

        super(ConfigContext, self).__init__(
            command_line_context.input_dir,
            command_line_context.output_file_path,
            command_line_context.force,
            command_line_context.config_file_path
        )
        self.parent = command_line_context
        self.fields = fields
        self.filesets = filesets

    def __str__(self):
        return "ConfigContext(%s, %s, %s)" % (self.parent, self.fields, self.filesets)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.parent == other.parent,
            self.fields == other.fields,
            self.filesets == other.filesets
        ])
