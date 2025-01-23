"""
ConvertDateFormatTask module.
"""

import datetime

import pytz

from dataunifier.common import constants as commonconstants
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_CONVERT_DATE_FORMAT = "convert_date_format"
K_FIELDS = "fields"
K_ACCEPTED_FORMATS = "accepted_formats"
K_TARGET_FORMAT = "target_format"
K_ALLOW_BLANK = "allow_blank"
K_TIMEZONE = "timezone"


def _validate_field_mapping(convert_date_format_task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in convert_date_format_task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" was expected by %s task "%s", but was not found in resulting fields ' \
                  'from %s task "%s". (File "%s")' % (
                      field, K_CONVERT_DATE_FORMAT, convert_date_format_task.name, previous_task.get_task_type_string(),
                      previous_task.name, current_file
                  )
            raise ConfigException(msg)


def _get_fields(task_parsing_context):
    fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
    return [ctxt.value for ctxt in fields_ctxt.value]


def _get_accepted_formats(task_parsing_context):
    accepted_formats_ctxt = confighelper.get_literal_list(task_parsing_context, K_ACCEPTED_FORMATS, True)
    return [ctxt.value for ctxt in accepted_formats_ctxt.value]


def _raise_unknown_timezone_exception(task_parsing_context, timezone):
    msg = f'Invalid timezone provided for {K_CONVERT_DATE_FORMAT} task "{task_parsing_context.task_name}": ' \
          f'"{timezone}". (File "{task_parsing_context.current_file}")'
    raise ConfigException(msg)


class ConvertDateFormatTask(AbstractRegularTask):
    """
    Task for interpreting date values and rewriting them in another format.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS, K_ACCEPTED_FORMATS, K_TARGET_FORMAT, K_ALLOW_BLANK, K_TIMEZONE}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields = _get_fields(task_parsing_context)
        accepted_formats = _get_accepted_formats(task_parsing_context)
        target_format = confighelper.get_literal(task_parsing_context, K_TARGET_FORMAT, True).value
        allow_blank = confighelper.get_boolean(task_parsing_context, K_ALLOW_BLANK, True).value
        timezone_ctxt = confighelper.get_literal(task_parsing_context, K_TIMEZONE, False)
        timezone = timezone_ctxt.value if timezone_ctxt else commonconstants.DEFAULT_TIMEZONE
        try:
            task = ConvertDateFormatTask(
                name, when, resulting_fields, fields, accepted_formats, target_format, allow_blank, timezone
            )
            _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
            return task
        except pytz.exceptions.UnknownTimeZoneError:
            _raise_unknown_timezone_exception(task_parsing_context, timezone)

    @classmethod
    def get_task_type_string(cls):
        return K_CONVERT_DATE_FORMAT

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, accepted_formats, target_format, allow_blank,
                 timezone=commonconstants.DEFAULT_TIMEZONE):
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.accepted_formats = accepted_formats
        self.target_format = target_format
        self.allow_blank = allow_blank
        self.timezone = pytz.timezone(timezone)
        super(ConvertDateFormatTask, self).__init__(name, when)

    def __str__(self):
        return "ConvertDateFormatTask(%s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.fields,
            self.accepted_formats, self.target_format, self.allow_blank,
            self.timezone
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return super(ConvertDateFormatTask, self).__eq__(other) and all([
            self.resulting_fields == other.resulting_fields,
            self.fields == other.fields,
            self.accepted_formats == other.accepted_formats,
            self.target_format == other.target_format,
            self.allow_blank == other.allow_blank,
            self.timezone == other.timezone
        ])

    def __transform_individual(self, value):
        if self.allow_blank and not value:
            return value
        for date_format in self.accepted_formats:
            try:
                dt = datetime.datetime.strptime(value, date_format)
                dt = self.timezone.localize(dt)
                return dt.strftime(self.target_format)
            except ValueError:
                pass
        raise ValueError()

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s".' % field)
            original_value = rowdict[field]
            try:
                transformed_value = self.__transform_individual(original_value)
                output[field] = transformed_value
            except ValueError:
                raise TransformationException('Could not interpret date value "%s" in field "%s".' % (
                    original_value, field
                ))
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
