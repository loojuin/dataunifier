"""
FuzzyMatchReplaceTask module.
"""

import abc

from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_FUZZY_MATCH_REPLACE = "fuzzy_match_replace"
K_FIELDS = "fields"
K_METHOD = "method"
K_RULES = "rules"
K_MINIMUM_SCORE = "minimum_score"
K_ON_UNMATCHED = "on_unmatched"
K_STRING = "string"
K_REPLACEMENT = "replacement"
K_NGRAM_SIZE = "ngram_size"

E_JACCARD = "jaccard"

E_FAIL = "fail"
E_PASSTHROUGH = "passthrough"
E_BLANK = "blank"

DEFAULT_NGRAM_SIZE = 3
DEFAULT_MINIMUM_SCORE = 0.0


class AbstractRule(abc.ABC):
    """
    Abstract base class for a fuzzy matching rule.
    """

    def __init__(self, string, replacement):
        """
        Super constructor for all rule classes.

        :param str string: The string to match against.
        :param str replacement: The replacement string.
        """

        self.string = string
        self.replacement = replacement

    @abc.abstractmethod
    def evaluate(self, string):
        """
        Evaluate how similar an input string is to the preconfigured string.

        :param str string: The input string.
        :return: A numerical score representing the similarity.
        :rtype: float
        """


class JaccardRule(AbstractRule):
    """
    A matching rule that uses the Jaccard method for matching strings.

    The Jaccard method works as such:
    1. Break each string into equal-sized n-grams of characters
    2. The similarity score is computed as the number of unqie n-grams that are in both strings, divided by the total
       number of unique n-grams.
    """

    def __init__(self, string, replacement, ngram_size):
        """
        Create a :code:`JaccardRule`.

        :param str string: The string to match against.
        :param str replacement: The replacement string.
        :param int ngram_size: The size of the n-grams to break the string into.
        """

        super(JaccardRule, self).__init__(string, replacement)
        self.ngram_size = ngram_size
        self.ngrams = self.ngramify(string)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.string == other.string,
            self.replacement == other.replacement,
            self.ngram_size == other.ngram_size
        ])

    def ngramify(self, string):
        """
        Turn a string into a set of n-grams.

        :param str string: The string to turn into n-grams.
        :return: A set of n-grams.
        :rtype: Set[str]
        """

        cleaned_string = string  # re.sub('[^A-Za-z0-9 ]', "", string)
        if len(cleaned_string) <= self.ngram_size:
            return {cleaned_string}
        return {cleaned_string[i:i + self.ngram_size] for i in range(len(cleaned_string) - self.ngram_size + 1)}

    def evaluate(self, string):
        input_set = self.ngramify(string)
        intersection = len(input_set & self.ngrams)
        union = len(input_set | self.ngrams)
        return intersection / union


def _get_method(task_parsing_context):
    method_ctxt = confighelper.get_literal(task_parsing_context, K_METHOD, False)
    method = method_ctxt.value if method_ctxt else E_JACCARD
    accepted_values = [E_JACCARD]
    if method not in accepted_values:
        raise ConfigException('Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
            method_ctxt.key_path, method, '", "'.join(accepted_values), method_ctxt.current_file
        ))
    return method


def _get_rules(task_parsing_context, method):  # pylint: disable=unused-argument
    rules_ctxt = confighelper.get_dict_list(task_parsing_context, K_RULES, True)
    ngram_size_ctxt = confighelper.get_literal(task_parsing_context, K_NGRAM_SIZE, False)
    ngram_size_str = ngram_size_ctxt.value if ngram_size_ctxt else DEFAULT_NGRAM_SIZE
    try:
        ngram_size = int(ngram_size_str)
        if ngram_size < 1:
            raise ValueError
        rules = []
        for rule_ctxt in rules_ctxt.value:
            string_ctxt = confighelper.get_literal_list(rule_ctxt, K_STRING, True)
            string_list = [ctxt.value for ctxt in string_ctxt.value]
            replacement = confighelper.get_literal(rule_ctxt, K_REPLACEMENT, True).value
            for string in string_list:
                rules.append(JaccardRule(string, replacement, ngram_size))
        return rules
    except ValueError:
        raise ConfigException('Invalid %s: "%s". Must be an integer more than 0. (File "%s", Task "%s")' % (
            K_NGRAM_SIZE, ngram_size_str, ngram_size_ctxt.current_file, task_parsing_context.task_name
        ))


def _get_minimum_score(task_parsing_context):
    minimum_score_ctxt = confighelper.get_literal(task_parsing_context, K_MINIMUM_SCORE, False)
    minimum_score = minimum_score_ctxt.value if minimum_score_ctxt else DEFAULT_MINIMUM_SCORE
    return minimum_score


def _get_on_unmatched(task_parsing_ctxt):
    on_unmatched_ctxt = confighelper.get_literal(task_parsing_ctxt, K_ON_UNMATCHED, True)
    value = on_unmatched_ctxt.value
    valid_values = [E_FAIL, E_BLANK, E_PASSTHROUGH]
    if value not in valid_values:
        raise ConfigException('Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
            on_unmatched_ctxt.key_path, value, '", "'.join(valid_values), on_unmatched_ctxt.current_file
        ))
    return value


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  '%s task "%s". (File "%s")' % (
                      field, K_FUZZY_MATCH_REPLACE, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class FuzzyMatchReplaceTask(AbstractRegularTask):
    """
    Task that replaces field values by evaluating how similar the value is to a predefined set of strings.
    """

    E_JACCARD = E_JACCARD
    E_FAIL = E_FAIL
    E_BLANK = E_BLANK
    E_PASSTHROUGH = E_PASSTHROUGH

    DEFAULT_NGRAM_SIZE = DEFAULT_NGRAM_SIZE
    DEFAULT_MINIMUM_SCORE = DEFAULT_MINIMUM_SCORE

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS, K_METHOD, K_RULES, K_MINIMUM_SCORE, K_ON_UNMATCHED, K_NGRAM_SIZE}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        fields = [ctxt.value for ctxt in fields_ctxt.value]
        method = _get_method(task_parsing_context)
        rules = _get_rules(task_parsing_context, method)
        minimum_score = _get_minimum_score(task_parsing_context)
        on_unmatched = _get_on_unmatched(task_parsing_context)
        task = FuzzyMatchReplaceTask(name, when, resulting_fields, fields, method, rules, minimum_score, on_unmatched)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_FUZZY_MATCH_REPLACE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, method, rules, minimum_score, on_unmatched):
        super(FuzzyMatchReplaceTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.method = method
        self.rules = rules
        self.minimum_score = minimum_score
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
            self.method == other.method,
            self.rules == other.rules,
            self.minimum_score == other.minimum_score,
            self.on_unmatched == other.on_unmatched
        ])

    def __find_most_matching_rule(self, value):
        most_matching_rule = None
        highest_score = 0.0
        for rule in self.rules:
            score = rule.evaluate(value)
            if score > highest_score:
                highest_score = score
                most_matching_rule = rule
        return most_matching_rule, highest_score

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s".' % field)
            value = rowdict[field]
            most_matching_rule, highest_score = self.__find_most_matching_rule(value)
            if most_matching_rule is None or highest_score < self.minimum_score:
                if self.on_unmatched == E_FAIL:
                    raise TransformationException(
                        'Could not match value "%s" in field "%s" to any rules.' % (value, field)
                    )
                if self.on_unmatched == E_BLANK:
                    output[field] = ""
            else:
                output[field] = most_matching_rule.replacement
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
