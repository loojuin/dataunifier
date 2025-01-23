"""
CsvLookupReplaceTask module.
"""

import csv
import os

from dataunifier.common import constants as commonconstants
from dataunifier.common.exceptions import TransformationException, ConfigException, NoSuchDirectoryException, \
    NoFileMatchingRegexException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper, fileio, display
from dataunifier.utils.display import ProgressBar

K_CSV_LOOKUP_REPLACE = "csv_lookup_replace"
K_FIELDS = "fields"
K_DIRECTORY = "directory"
K_FILENAME_REGEX = "filename_regex"
K_LOOKUP_COLUMN = "lookup_column"
K_VALUE_COLUMN = "value_column"
K_ON_UNMATCHED = "on_unmatched"
K_DEDUPLICATE_BY = "deduplicate_by"

E_FAIL = "fail"
E_PASSTHROUGH = "passthrough"
E_BLANK = "blank"
E_LOWER_ROW_NUMBER = "lower_row_number"
E_HIGHER_ROW_NUMBER = "higher_row_number"


def _parse_on_unmatched(on_unmatched_ctxt):
    value = on_unmatched_ctxt.value
    valid_values = [E_FAIL, E_BLANK, E_PASSTHROUGH]
    if value not in valid_values:
        raise ConfigException('Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
            on_unmatched_ctxt.key_path, value, '", "'.join(valid_values), on_unmatched_ctxt.current_file
        ))
    return value


def _get_lookup_file_path(task_parsing_context):
    directory_ctxt = confighelper.get_literal(task_parsing_context, K_DIRECTORY, True)
    directory_raw = directory_ctxt.value
    directory = confighelper.handle_placeholder_values_and_clean(directory_ctxt, directory_raw)
    filename_regex = confighelper.get_literal(task_parsing_context, K_FILENAME_REGEX, True).value
    try:
        filenames = fileio.get_file_names_by_regex(directory, filename_regex)
        if len(filenames) > 1:
            msg = 'Found multiple files matching pattern "%s" for %s task "%s": "%s" (File "%s")' % (
                filename_regex, K_CSV_LOOKUP_REPLACE, task_parsing_context.task_name, '", "'.join(filenames),
                task_parsing_context.current_file
            )
            raise ConfigException(msg)
        return os.path.join(directory, filenames[0])
    except NoSuchDirectoryException:
        msg = 'Directory "%s" was specified in %s task "%s" but could not be found. (File "%s")' % (
            directory, K_CSV_LOOKUP_REPLACE, task_parsing_context.task_name, task_parsing_context.current_file
        )
        raise ConfigException(msg)
    except NoFileMatchingRegexException:
        msg = 'Could not find any files matching pattern "%s" for %s task "%s". (File "%s")' % (
            filename_regex, K_CSV_LOOKUP_REPLACE, task_parsing_context.task_name, task_parsing_context.current_file
        )
        raise ConfigException(msg)


def _get_deduplicate_by(task_parsing_context):
    deduplicate_by_ctxt = confighelper.get_literal(task_parsing_context, K_DEDUPLICATE_BY, False)
    deduplicate_by = deduplicate_by_ctxt.value if deduplicate_by_ctxt else None
    if deduplicate_by is not None:
        valid_values = [E_HIGHER_ROW_NUMBER, E_LOWER_ROW_NUMBER]
        if deduplicate_by not in valid_values:
            msg = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                deduplicate_by_ctxt.key_path, deduplicate_by,
                '", "'.join(valid_values), deduplicate_by_ctxt.current_file
            )
            raise ConfigException(msg)
    return deduplicate_by


def _raise_missing_column_exception(task_parsing_context, file_path, column_name):
    msg = 'File "%s" does not contain column "%s", required by %s task %s. (File "%s")' % (
        file_path, column_name, K_CSV_LOOKUP_REPLACE, task_parsing_context.task_name, task_parsing_context.current_file
    )
    raise ConfigException(msg)


def _raise_duplicate_lookup_exception(task_parsing_context, file_path, column_name, value):
    msg = 'Duplicate value "%s" found in lookup column "%s" of file "%s", when preparing %s task "%s" ' \
          '(File "%s")' % (
              value, column_name, file_path, K_CSV_LOOKUP_REPLACE, task_parsing_context.task_name,
              task_parsing_context.current_file
          )
    raise ConfigException(msg)


def _get_lookup_dict(task_parsing_context, deduplicate_by):
    task_name = task_parsing_context.task_name
    lookup_col = confighelper.get_literal(task_parsing_context, K_LOOKUP_COLUMN, True).value
    value_col = confighelper.get_literal(task_parsing_context, K_VALUE_COLUMN, True).value
    file_path = _get_lookup_file_path(task_parsing_context)
    row_count = fileio.count_rows(file_path)
    lookup_dict = {}
    with open(file_path, "r", encoding=commonconstants.DEFAULT_ENCODING) as f:
        display.stdout('Parsing file "%s" for %s task "%s"' % (file_path, K_CSV_LOOKUP_REPLACE, task_name))
        progress_bar = ProgressBar(row_count)
        reader = csv.DictReader(f)
        for rowdict in reader:
            if lookup_col not in rowdict:
                _raise_missing_column_exception(task_parsing_context, file_path, lookup_col)
            if value_col not in rowdict:
                _raise_missing_column_exception(task_parsing_context, file_path, value_col)
            lookup = rowdict[lookup_col]
            value = rowdict[value_col]
            if lookup in lookup_dict:
                if deduplicate_by is None:
                    _raise_duplicate_lookup_exception(task_parsing_context, file_path, lookup_col, lookup)
                elif deduplicate_by == E_HIGHER_ROW_NUMBER:
                    lookup_dict[lookup] = value
            else:
                lookup_dict[lookup] = value
            progress_bar.increment()
        progress_bar.close()
    return lookup_dict


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  'preceding %s task "%s". (File "%s")' % (
                      field, K_CSV_LOOKUP_REPLACE, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class CsvLookupReplaceTask(AbstractRegularTask):
    """
    Replaces values by looking for them in a CSV file, and replacing them with the value from another column on the
    same row.
    """

    E_PASSTHROUGH = E_PASSTHROUGH
    E_BLANK = E_BLANK
    E_FAIL = E_FAIL

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {
            K_FIELDS, K_DIRECTORY, K_FILENAME_REGEX, K_LOOKUP_COLUMN, K_VALUE_COLUMN, K_ON_UNMATCHED, K_DEDUPLICATE_BY
        }
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        fields = [ctxt.value for ctxt in fields_ctxt.value]
        deduplicate_by = _get_deduplicate_by(task_parsing_context)
        lookup_dict = _get_lookup_dict(task_parsing_context, deduplicate_by)
        on_unmatched = _parse_on_unmatched(confighelper.get_literal(task_parsing_context, K_ON_UNMATCHED, True))
        task = CsvLookupReplaceTask(name, when, resulting_fields, fields, lookup_dict, on_unmatched)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_CSV_LOOKUP_REPLACE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, lookup_dict, on_unmatched):
        super(CsvLookupReplaceTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.lookup_dict = lookup_dict
        self.on_unmatched = on_unmatched

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
            self.lookup_dict == other.lookup_dict,
            self.on_unmatched == other.on_unmatched
        ])

    def __str__(self):
        return "CsvLookupReplaceTask(%s, %s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.fields, self.lookup_dict, self.on_unmatched
        )

    def __repr__(self):
        return str(self)

    def __transform_individual(self, value):
        if value not in self.lookup_dict:
            if self.on_unmatched == E_BLANK:
                return ""
            if self.on_unmatched == E_PASSTHROUGH:
                return value
            raise ValueError()
        return self.lookup_dict[value]

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s".' % field)
            try:
                output[field] = self.__transform_individual(rowdict[field])
            except ValueError:
                raise TransformationException('Encountered unrecognised value in field "%s": "%s"' % (
                    field, rowdict[field]
                ))
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
