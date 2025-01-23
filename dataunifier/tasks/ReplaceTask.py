"""
ReplaceTask module.
"""

from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_REPLACE = "replace"
K_FIELDS = "fields"
K_ON_UNMATCHED = "on_unmatched"
K_ALLOW_BLANK = "allow_blank"
K_RULES = "rules"
K_WITH = "with"

E_FAIL = "fail"
E_PASSTHROUGH = "passthrough"
E_BLANK = "blank"


class ReplaceRule:
    """
    A single replacement rule.
    """

    def __init__(self, string_list, replacement):
        """
        Create a replacement rule.

        :param list[str] | set[str] string_list: The collection of strings to match against.
        :param str replacement: The replacement string.
        """

        self.string_list = string_list
        self.replacement = replacement

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.string_list == other.string_list,
            self.replacement == other.replacement
        ])

    def __str__(self):
        return f"ReplaceRule({self.string_list} => {self.replacement})"

    def __repr__(self):
        return str(self)


def _get_fields(task_parsing_context):
    return [ctxt.value for ctxt in confighelper.get_literal_list(task_parsing_context, K_FIELDS, True).value]


def _get_on_unmatched(task_parsing_context):
    value = confighelper.get_literal(task_parsing_context, K_ON_UNMATCHED, True).value
    valid_values = [E_BLANK, E_PASSTHROUGH, E_FAIL]
    if value not in valid_values:
        raise ConfigException('Invalid value for key "%s" in task "%s": "%s". Accepted values are: "%s".'
                              '(File "%s")' % (
                                  K_ON_UNMATCHED, task_parsing_context.task_name, value, '", "'.join(valid_values),
                                  task_parsing_context.current_file
                              ))
    return value


def _get_allow_blank(task_parsing_context):
    return confighelper.get_boolean(task_parsing_context, K_ALLOW_BLANK, True).value


def _parse_rules(rules_ctxt):
    output = []
    for rule_ctxt in rules_ctxt.value:
        string_list = [ctxt.value for ctxt in confighelper.get_literal_list(rule_ctxt, K_REPLACE, True).value]
        replacement = confighelper.get_literal(rule_ctxt, K_WITH, True).value
        output.append(ReplaceRule(string_list, replacement))
    return output


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  '%s task "%s". (File "%s")' % (
                      field, K_REPLACE, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


def _create_dict_from_rules(rules):
    output = {}
    for rule in rules:
        for string in rule.string_list:
            if string not in output:
                output[string] = rule.replacement
    return output


class ReplaceTask(AbstractRegularTask):
    """
    Task that replacement field values according to a predefined mapping.
    """

    E_FAIL = E_FAIL
    E_PASSTHROUGH = E_PASSTHROUGH
    E_BLANK = E_BLANK

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS, K_ON_UNMATCHED, K_ALLOW_BLANK, K_RULES}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields = _get_fields(task_parsing_context)
        on_unmatched = _get_on_unmatched(task_parsing_context)
        allow_blank = _get_allow_blank(task_parsing_context)
        rules_ctxt = confighelper.get_dict_list(task_parsing_context, K_RULES, True)
        rules = _parse_rules(rules_ctxt)
        rules_file = rules_ctxt.current_file
        task = ReplaceTask(name, when, resulting_fields, fields, on_unmatched, allow_blank, rules, rules_file)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_REPLACE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, on_unmatched, allow_blank, rules, rules_file):
        super(ReplaceTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.on_unmatched = on_unmatched
        self.allow_blank = allow_blank
        self.d = _create_dict_from_rules(rules)
        self.rules_file = rules_file

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
            self.on_unmatched == other.on_unmatched,
            self.allow_blank == other.allow_blank,
            self.d == other.d,
            self.rules_file == other.rules_file
        ])

    def __str__(self):
        return f"ReplaceTask({self.name}, {self.when}, {self.resulting_fields}, {self.fields}, " \
               f"{self.on_unmatched}, {self.allow_blank}, {self.d}, {self.rules_file})"

    def __repr__(self):
        return str(self)

    def __transform_individual(self, value):
        if value in self.d:
            return self.d[value]
        raise ValueError()

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException(f'Could not find field "{field}".')
            if not(self.allow_blank and not rowdict[field]):
                try:
                    output[field] = self.__transform_individual(rowdict[field])
                except ValueError:
                    if self.on_unmatched == E_FAIL:
                        msg = 'Encountered unrecognised value in field "%s": "%s". (Rules in file "%s")' % (
                            field, rowdict[field], self.rules_file
                        )
                        raise TransformationException(msg)
                    if self.on_unmatched == E_BLANK:
                        output[field] = ""
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
