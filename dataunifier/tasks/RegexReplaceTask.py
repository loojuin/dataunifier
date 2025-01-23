"""
RegexReplaceTask module.
"""

import re

from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_REGEX_REPLACE = "regex_replace"
K_FIELDS = "fields"
K_ON_UNMATCHED = "on_unmatched"
K_ALLOW_BLANK = "allow_blank"
K_RULES = "rules"
K_REPLACE = "replace"
K_WITH = "with"

E_FAIL = "fail"
E_BLANK = "blank"
E_PASSTHROUGH = "passthrough"


class RegexReplaceRule:
    """
    A single replacement rule.
    """

    def __init__(self, pattern_list, replacement):
        """
        Create a replacement rule.

        :param list[re.Pattern] pattern_list: A list of precompiled patterns to match against.
        :param str replacement: The replacement string.
        """

        self.pattern_list = pattern_list
        self.replacement = replacement

    def __str__(self):
        return "RegexReplaceRule(%s => %s)" % (self.pattern_list, self.replacement)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.pattern_list == other.pattern_list,
            self.replacement == other.replacement
        ])


def _parse_on_unmatched(task_parsing_context):
    on_unmatched_ctxt = confighelper.get_literal(task_parsing_context, K_ON_UNMATCHED, True)
    value = on_unmatched_ctxt.value
    valid_values = [E_FAIL, E_BLANK, E_PASSTHROUGH]
    if value not in valid_values:
        raise ConfigException('Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
            on_unmatched_ctxt.key_path, value, '", "'.join(valid_values), on_unmatched_ctxt.current_file
        ))
    return value


def _parse_pattern_list(regex_list_ctxt):
    regex_ctxt_list = regex_list_ctxt.value
    output = []
    for regex_ctxt in regex_ctxt_list:
        regex = regex_ctxt.value
        try:
            output.append(re.compile(regex))
        except re.error as e:
            msg = 'Invalid regular expression at key "%s": "%s". Details: "%s" (File "%s")' % (
                regex_ctxt.key_path, regex, str(e), regex_ctxt.current_file
            )
            raise ConfigException(msg)
    return output


def _parse_rules(rules_ctxt):
    output = []
    for rule_ctxt in rules_ctxt.value:
        regex_list_ctxt = confighelper.get_literal_list(rule_ctxt, K_REPLACE, True)
        pattern_list = _parse_pattern_list(regex_list_ctxt)
        replacement_ctxt = confighelper.get_literal(rule_ctxt, K_WITH, True)
        replacement = replacement_ctxt.value
        output.append(RegexReplaceRule(pattern_list, replacement))
    return output


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  '%s task "%s". (File "%s")' % (
                      field, K_REGEX_REPLACE, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class RegexReplaceTask(AbstractRegularTask):
    """
    Task that replaces field values using regular expressions.
    """

    E_FAIL = E_FAIL
    E_BLANK = E_BLANK
    E_PASSTHROUGH = E_PASSTHROUGH

    @classmethod
    def create_from_config(cls, task_parsing_context):
        task_name = task_parsing_context.task_name
        when = task_parsing_context.when
        valid_keys = {K_FIELDS, K_ON_UNMATCHED, K_ALLOW_BLANK, K_RULES}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        resulting_fields = task_parsing_context.previous_task.get_resulting_fields()
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        fields = [ctxt.value for ctxt in fields_ctxt.value]
        on_unmatched = _parse_on_unmatched(task_parsing_context)
        allow_blank = confighelper.get_boolean(task_parsing_context, K_ALLOW_BLANK, True).value
        rules_ctxt = confighelper.get_dict_list(task_parsing_context, K_RULES, True)
        rules = _parse_rules(rules_ctxt)
        rules_file = rules_ctxt.current_file
        task = RegexReplaceTask(
            task_name, when, resulting_fields, fields, on_unmatched, allow_blank, rules, rules_file
        )
        _validate_field_mapping(task, task_parsing_context.previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_REGEX_REPLACE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, on_unmatched, allow_blank, rules, rules_file):
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.on_unmatched = on_unmatched
        self.allow_blank = allow_blank
        self.rules = rules
        self.rules_file = rules_file
        super(RegexReplaceTask, self).__init__(name, when)

    def __str__(self):
        return "RegexReplaceTask(%s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.fields, self.on_unmatched,
            self.allow_blank, self.rules, self.rules_file
        )

    def __repr__(self):
        return str(self)

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
            self.rules == other.rules,
            self.rules_file == other.rules_file
        ])

    def __transform_individual(self, value):
        for rule in self.rules:
            for pattern in rule.pattern_list:
                if pattern.search(value):
                    return pattern.sub(rule.replacement, value)
        raise ValueError()

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s".' % field)
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
