"""
Classes pertaining to parsing of command line arguments.
"""


class CommandLineContext:
    """
    Context class containing command line arguments.
    """

    def __init__(self, input_dir, output_file_path, force, config_file_path):
        """
        Create a :code:`CommandLineContext` object.

        :param str input_dir: The input directory path.
        :param str output_file_path: The output file path.
        :param bool force: Indicates whether to forcefully overwrite the output file if it exists.
        :param str config_file_path: The configuration file path.
        """

        self.input_dir = input_dir
        self.output_file_path = output_file_path
        self.force = force
        self.config_file_path = config_file_path

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.input_dir == other.input_dir,
            self.output_file_path == other.output_file_path,
            self.force == other.force,
            self.config_file_path == other.config_file_path
        ])

    def __hash__(self):
        return hash((self.input_dir, self.output_file_path, self.force, self.config_file_path))

    def __str__(self):
        return "CommandLineContext(%s, %s, %s, %s)" % (
            self.input_dir, self.output_file_path, str(self.force), self.config_file_path
        )

    def __repr__(self):
        return str(self)
