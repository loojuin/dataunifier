"""
CsvMatchTask module.
"""

import csv
import os

from dataunifier.common import constants as commonconstants
from dataunifier.common.exceptions import TransformationException, ConfigException, NoSuchDirectoryException, \
    NoFileMatchingRegexException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper, fileio, display
from dataunifier.utils.display import ProgressBar

K_CSV_MATCH = "csv_match"
K_FIELDS = "fields"
K_DIRECTORY = "directory"
K_FILENAME_REGEX = "filename_regex"
K_LOOKUP_COLUMN = "lookup_column"
K_MATCH_VALUE = "match_value"
K_UNMATCH_VALUE = "unmatch_value"


def _get_lookup_file_path(task_parsing_context):
    directory_ctxt = confighelper.get_literal(task_parsing_context, K_DIRECTORY, True)
    directory_raw = directory_ctxt.value
    directory = confighelper.handle_placeholder_values_and_clean(directory_ctxt, directory_raw)
    filename_regex = confighelper.get_literal(task_parsing_context, K_FILENAME_REGEX, True).value
    try:
        filenames = fileio.get_file_names_by_regex(directory, filename_regex)
        if len(filenames) > 1:
            msg = 'Found multiple files matching pattern "%s" for %s task "%s": "%s" (File "%s")' % (
                filename_regex, K_CSV_MATCH, task_parsing_context.task_name, '", "'.join(filenames),
                task_parsing_context.current_file
            )
            raise ConfigException(msg)
        return os.path.join(directory, filenames[0])
    except NoSuchDirectoryException:
        msg = 'Directory "%s" was specified in %s task "%s" but could not be found. (File "%s")' % (
            directory, K_CSV_MATCH, task_parsing_context.task_name, task_parsing_context.current_file
        )
        raise ConfigException(msg)
    except NoFileMatchingRegexException:
        msg = 'Could not find any files matching pattern "%s" for %s task "%s". (File "%s")' % (
            filename_regex, K_CSV_MATCH, task_parsing_context.task_name, task_parsing_context.current_file
        )
        raise ConfigException(msg)


def _get_lookup_set(task_parsing_context):
    task_name = task_parsing_context.task_name
    lookup_column = confighelper.get_literal(task_parsing_context, K_LOOKUP_COLUMN, True).value
    file_path = _get_lookup_file_path(task_parsing_context)
    row_count = fileio.count_rows(file_path)
    lookup_set = set()
    with open(file_path, "r", encoding=commonconstants.DEFAULT_ENCODING) as f:
        display.stdout('Parsing file "%s" for %s task "%s"' % (file_path, K_CSV_MATCH, task_name))
        progress_bar = ProgressBar(row_count)
        reader = csv.DictReader(f)
        for rowdict in reader:
            if lookup_column not in rowdict:
                msg = 'File "%s" does not contain lookup column "%s", required by %s task %s. (File "%s")' % (
                    file_path, lookup_column, K_CSV_MATCH, task_parsing_context.task_name,
                    task_parsing_context.current_file
                )
                raise ConfigException(msg)
            lookup_set.add(rowdict[lookup_column])
            progress_bar.increment()
        progress_bar.close()
    return lookup_set


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  'preceding %s task "%s". (File "%s")' % (
                      field, K_CSV_MATCH, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class CsvMatchTask(AbstractRegularTask):
    """
    Changes a value to one or another depending on whether it can be found inside a CSV file.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS, K_DIRECTORY, K_FILENAME_REGEX, K_LOOKUP_COLUMN, K_MATCH_VALUE, K_UNMATCH_VALUE}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        fields = [ctxt.value for ctxt in fields_ctxt.value]
        lookup_set = _get_lookup_set(task_parsing_context)
        match_value = confighelper.get_literal(task_parsing_context, K_MATCH_VALUE, True).value
        unmatch_value = confighelper.get_literal(task_parsing_context, K_UNMATCH_VALUE, True).value
        task = CsvMatchTask(name, when, resulting_fields, fields, lookup_set, match_value, unmatch_value)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_CSV_MATCH

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, lookup_set, match_value, unmatch_value):
        super(CsvMatchTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.lookup_set = lookup_set
        self.match_value = match_value
        self.unmatch_value = unmatch_value

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when,
            self.resulting_fields == other.resulting_fields,
            self.fields == other.fields,
            self.lookup_set == other.lookup_set,
            self.match_value == other.match_value,
            self.unmatch_value == other.unmatch_value
        ])

    def __str__(self):
        return "CsvMatchTask(%s, %s, %s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.fields, self.lookup_set, self.match_value,
            self.unmatch_value
        )

    def __repr__(self):
        return str(self)

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s".' % field)
            value = rowdict[field]
            output[field] = self.match_value if value in self.lookup_set else self.unmatch_value
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
