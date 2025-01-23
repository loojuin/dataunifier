"""
Classes pertaining to parsing of input data files.
"""

import csv

from dataunifier.cmdline.classes import CommandLineContext


class TestBogusDictWriter(csv.DictWriter):
    """
    A class for use in unit testing that behaves like a :code:`DictWriter` but simply stores written rowdicts
    instead of writing them to a file.
    """

    class TestBogusWriter:
        """
        A mock writer class for use in testing.
        """

        def __init__(self):
            pass

        def write(self):
            """
            Write text.
            """

    def __init__(self, string):
        """
        Create a :code:`TestBogusDictWriter` object.

        :param str string: An arbitrary string that helps distinguish this writer object from others.
        """

        self.string = string
        self.rowdicts = []
        super(TestBogusDictWriter, self).__init__(self.TestBogusWriter(), [])

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return self.string == other.string

    def writerow(self, rowdict):
        """
        Write a single rowdict.

        :param dict rowdict: The rowdict to write.
        """

        self.rowdicts.append(rowdict)

    def writerows(self, rowdicts):
        """
        Write multiple rowdicts.

        :param list[Dict] rowdicts: The rowdicts to write.
        """
        self.rowdicts.extend(rowdicts)


class ParseFilesetContext(CommandLineContext):
    """
    Contains contextual information when parsing a :code:`Fileset`.
    """

    def __init__(self, command_line_context, writer, fileset):
        """
        Create a :code:`ParseFilesetContext` object.

        :param CommandLineContext command_line_context: The underlying command line context.
        :param csv.DictWriter writer: The DictWriter to use to write rows out.
        :param Fileset fileset: The fileset currently being parsed.
        """

        super(ParseFilesetContext, self).__init__(
            command_line_context.input_dir,
            command_line_context.output_file_path,
            command_line_context.force,
            command_line_context.config_file_path
        )
        self.parent = command_line_context
        self.writer = writer
        self.fileset = fileset

    def __str__(self):
        return "ParseFilesetContext(%s, %s, %s)" % (
            self.parent, self.writer, self.fileset
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
            self.writer == other.writer,
            self.fileset == other.fileset
        ])


class ParseInputFileContext(ParseFilesetContext):
    """
    Contains contextual information when parsing an :code:`InputFile`.
    """

    def __init__(self, parse_fileset_ctxt, input_file):
        """
        Create a :code:`ParseInputFileContext` object.

        :param ParseFilesetContext parse_fileset_ctxt: The underlying context object.
        :param InputFile input_file: The InputFile currently being parsed.
        """

        super(ParseInputFileContext, self).__init__(
            parse_fileset_ctxt.parent,
            parse_fileset_ctxt.writer,
            parse_fileset_ctxt.fileset
        )
        self.parent = parse_fileset_ctxt
        self.input_file = input_file

    def __str__(self):
        return "ParseInputFileContext(%s, %s)" % (self.parent, self.input_file)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.parent == other.parent,
            self.input_file == other.input_file
        ])


class ParseIteratorContext(ParseInputFileContext):
    """
    Contains contextual information when parsing an iterator of rowdicts.
    """

    def __init__(self, parse_input_file_ctxt, filepath, sheet, iterator):
        """
        Create a :code:`ParseIteratorContext` object.

        :param ParseInputFileContext parse_input_file_ctxt: The underlying context object.
        :param str filepath: The path of the file being parsed.
        :param Optional[str] sheet: The name of the sheet being parsed, or None if not applicable.
        :param csv.DictReader | list[dict] iterator: The actually iterable (such as a list of rowdicts) or iterator
                                                     (such as csv.DictReader) containing the rowdicts.
        """

        super(ParseIteratorContext, self).__init__(parse_input_file_ctxt.parent, parse_input_file_ctxt.input_file)
        self.parent = parse_input_file_ctxt
        self.filepath = filepath
        self.sheet = sheet
        self.iterator = iterator

    def __str__(self):
        return "ParseIteratorContext(%s, %s, %s, %s)" % (
            self.parent, self.filepath, self.sheet, self.iterator
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
            self.filepath == other.filepath,
            self.sheet == other.sheet,
            self.iterator == other.iterator
        ])


class ParseRowContext(ParseIteratorContext):
    """
    Contains contextual information for parsing of a single row.
    """

    def __init__(self, parse_iterator_ctxt, row_number, rowdict):
        """
        Create a :code:`ParseRowContext` object.

        :param ParseIteratorContext parse_iterator_ctxt: The underlying context object.
        :param int row_number: The row number of the current row being processed.
        :param dict rowdict: The actual rowdict being processed.
        """

        super(ParseRowContext, self).__init__(
            parse_iterator_ctxt.parent,
            parse_iterator_ctxt.filepath,
            parse_iterator_ctxt.sheet,
            parse_iterator_ctxt.iterator
        )
        self.parent = parse_iterator_ctxt
        self.row_number = row_number
        self.rowdict = rowdict

    def with_updated_rowdict(self, rowdict):
        """
        Produce a new context object identical to the original, except with a different rowdict.

        For use in the transformation process.

        :param dict rowdict: The new rowdict
        :return: The new object.
        :rtype: ParseRowContext
        """

        return ParseRowContext(self.parent, self.row_number, rowdict)

    def __str__(self):
        return "ParseRowContext(%s, %s, %s)" % (
            self.parent, self.row_number, self.rowdict
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
            self.row_number == other.row_number,
            self.rowdict == other.rowdict
        ])
