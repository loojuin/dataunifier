"""
MapFieldsTask module.
"""

from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_MAP_FIELDS = "map_fields"
K_FIELDS = "fields"
K_TARGET_FIELD = "target_field"
K_SRC_FIELDS = "src_fields"
K_MANDATORY = "mandatory"
K_IGNORE_CASE = "ignore_case"


class Field:
    """
    A single rule to map a field name.
    """

    def __init__(self, target_field, src_fields, mandatory, ignore_case):
        """
        Create a field mapping rule.

        :param str target_field: The output field name.
        :param list[str] | set[str] src_fields: A list of fields in the input data that should be changed.
        :param bool mandatory: Indicates whether the field is mandatory, i.e., whether the programme should fail if
                               none of the fields listed in src_fields is found in the data.
        :param bool ignore_case: Indicates whether the field matching is case-sensitive.
        """

        self.target_field = target_field
        self.src_fields = src_fields
        self.mandatory = mandatory
        self.ignore_case = ignore_case

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.target_field == other.target_field,
            self.src_fields == other.src_fields,
            self.mandatory == other.mandatory,
            self.ignore_case == other.ignore_case
        ])

    def __str__(self):
        return "Field([%s] => %s, %s, %s)" % (
            ", ".join(self.src_fields), self.target_field, self.mandatory, self.ignore_case
        )

    def __repr__(self):
        return str(self)


def _parse_field_dict(field_dict_ctxt, global_ignore_case):
    valid_keys = {K_TARGET_FIELD, K_SRC_FIELDS, K_MANDATORY, K_IGNORE_CASE}
    confighelper.check_invalid_keys(field_dict_ctxt, valid_keys)
    ignore_case_ctxt = confighelper.get_boolean(field_dict_ctxt, K_IGNORE_CASE, False)
    ignore_case = ignore_case_ctxt.value if ignore_case_ctxt else global_ignore_case
    target_field_ctxt = confighelper.get_literal(field_dict_ctxt, K_TARGET_FIELD, True)
    target_field = target_field_ctxt.value
    src_fields_ctxt = confighelper.get_literal_list(field_dict_ctxt, K_SRC_FIELDS, False)
    if ignore_case:
        src_fields = [ctxt.value.lower() for ctxt in src_fields_ctxt.value] if src_fields_ctxt else []
    else:
        src_fields = [ctxt.value for ctxt in src_fields_ctxt.value] if src_fields_ctxt else []
    mandatory_ctxt = confighelper.get_boolean(field_dict_ctxt, K_MANDATORY, False)
    mandatory = False if src_fields_ctxt is None else (mandatory_ctxt.value if mandatory_ctxt else True)
    return Field(target_field, src_fields, mandatory, ignore_case)


def _parse_field_dict_list(field_dict_list_ctxt, global_ignore_case):
    field_dict_ctxt_list = field_dict_list_ctxt.value
    return [_parse_field_dict(field_dict_ctxt, global_ignore_case) for field_dict_ctxt in field_dict_ctxt_list]


def _raise_clashing_field_exception(field1, field2, map_fields_task, previous_task, current_file):
    msg = '%s "%s" and "%s" in %s task "%s" map to the same %s and were both found in ' \
          'resulting fields of %s task "%s". (File "%s")' % (
              K_SRC_FIELDS, field1, field2, K_MAP_FIELDS, map_fields_task.name, K_TARGET_FIELD,
              previous_task.get_task_type_string(), previous_task.name, current_file
          )
    raise ConfigException(msg)


def _raise_missing_field_exception(fields, map_fields_task, previous_task, current_file):
    msg = 'Fields "%s" are expected by %s task "%s" but was not found in resulting fields of %s task "%s". ' \
          '(File "%s")' % (
              '" or "'.join(fields), K_MAP_FIELDS, map_fields_task.name, previous_task.get_task_type_string(),
              previous_task.name, current_file
          )
    raise ConfigException(msg)


def _validate_field_mapping(map_fields_task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields_set = set(previous_task.get_resulting_fields())
    for field in map_fields_task.fields:
        matched = None
        for src_field in field.src_fields:
            if src_field in previous_task_fields_set:
                if matched:
                    _raise_clashing_field_exception(matched, src_field, map_fields_task, previous_task, current_file)
                matched = src_field
        if not matched and field.mandatory:
            _raise_missing_field_exception(field.src_fields, map_fields_task, previous_task, current_file)


class MapFieldsTask(AbstractRegularTask):
    """
    Task for translating field names.
    """

    @classmethod
    def get_task_type_string(cls):
        return K_MAP_FIELDS

    @classmethod
    def is_conditional(cls):
        return False

    @classmethod
    def create_from_config(cls, task_parsing_context):
        task_name = task_parsing_context.task_name
        if task_parsing_context.when is not None:
            msg = '"when" cannot be used with a %s task. (File "%s", task "%s")' % (
                K_MAP_FIELDS, task_parsing_context.current_file, task_name
            )
            raise ConfigException(msg)
        valid_keys = {K_FIELDS, K_IGNORE_CASE}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        global_ignore_case_ctxt = confighelper.get_boolean(task_parsing_context, K_IGNORE_CASE, False)
        global_ignore_case = global_ignore_case_ctxt.value if global_ignore_case_ctxt else False
        field_dict_list_ctxt = confighelper.get_dict_list(task_parsing_context, K_FIELDS, True)
        fields = _parse_field_dict_list(field_dict_list_ctxt, global_ignore_case)
        task = MapFieldsTask(task_name, fields)
        _validate_field_mapping(task, task_parsing_context.previous_task, task_parsing_context.current_file)
        return task

    def __init__(self, name, fields):
        super(MapFieldsTask, self).__init__(name, None)
        self.fields = fields
        self.resulting_fields = [field.target_field for field in self.fields]

    def __str__(self):
        return "MapFieldsTask(%s, %s, %s)" % (
            self.name,
            self.when,
            self.fields
        )

    def __repr__(self):
        return str(self)

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        rowdict_ignore_case = {k.lower(): v for k, v in rowdict.items()}
        output = {}
        for field in self.fields:
            value = ""
            mapped = None
            rowdict_to_use = rowdict_ignore_case if field.ignore_case else rowdict
            for src_field in field.src_fields:
                if src_field in rowdict_to_use:
                    if mapped:
                        msg = 'Fields "%s" and "%s" both exist and are mapped to the same target field "%s"' % (
                            mapped, src_field, field.target_field
                        )
                        raise TransformationException(msg)
                    value = rowdict_to_use[src_field]
                    mapped = src_field
            if not mapped and field.mandatory:
                msg = 'Could not find any fields to map to target field "%s". Expected source fields: "%s"' % (
                    field.target_field, '", "'.join(field.src_fields)
                )
                raise TransformationException(msg)
            output[field.target_field] = value
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return super(MapFieldsTask, self).__eq__(other) and all([
            self.fields == other.fields,
            self.when == other.when
        ])
