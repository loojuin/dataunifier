"""
ArithmeticTask module.
"""

from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_ARITHMETIC = "arithmetic"
K_LEFT_FIELD = "left_field"
K_RIGHT_FIELD = "right_field"
K_RESULT_FIELD = "result_field"
K_OPERATION = "operation"
K_BLANK_IS_ZERO = "blank_is_zero"

E_ADD = "add"
E_SUBTRACT = "subtract"
E_MULTIPLY = "multiply"
E_DIVIDE = "divide"


def _get_numerical_value(rowdict, field, blank_is_zero):
    value_string = rowdict[field]
    if blank_is_zero and value_string == "":
        return 0
    try:
        return int(value_string)
    except ValueError:
        pass
    try:
        return float(value_string)
    except ValueError:
        raise TransformationException('Value of field "%s" is not a number: "%s"' % (field, value_string))


def _check_field_existence(rowdict, fields):
    for field in fields:
        if field not in rowdict:
            raise TransformationException('Could not find field "%s".' % field)


def _get_operation(task_parsing_context):
    operation_ctxt = confighelper.get_literal(task_parsing_context, K_OPERATION, True)
    operation = operation_ctxt.value
    valid_values = [E_ADD, E_SUBTRACT, E_MULTIPLY, E_DIVIDE]
    if operation not in valid_values:
        raise ConfigException('Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
            operation_ctxt.key_path, operation, '", "'.join(valid_values), operation_ctxt.current_file
        ))
    return operation


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    fields = [task.left_field, task.right_field, task.result_field]
    for field in fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  'preceding %s task "%s". (File "%s")' % (
                      field, K_ARITHMETIC, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class ArithmeticTask(AbstractRegularTask):
    """
    Task that performs arithmetic operations on field values and writes result to another field.
    """

    E_ADD = E_ADD
    E_SUBTRACT = E_SUBTRACT
    E_MULTIPLY = E_MULTIPLY
    E_DIVIDE = E_DIVIDE

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_LEFT_FIELD, K_RIGHT_FIELD, K_RESULT_FIELD, K_OPERATION, K_BLANK_IS_ZERO}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        left_field = confighelper.get_literal(task_parsing_context, K_LEFT_FIELD, True).value
        right_field = confighelper.get_literal(task_parsing_context, K_RIGHT_FIELD, True).value
        result_field = confighelper.get_literal(task_parsing_context, K_RESULT_FIELD, True).value
        operation = _get_operation(task_parsing_context)
        blank_is_zero_ctxt = confighelper.get_boolean(task_parsing_context, K_BLANK_IS_ZERO, False)
        blank_is_zero = blank_is_zero_ctxt.value if blank_is_zero_ctxt else False
        task = ArithmeticTask(
            name, when, resulting_fields, left_field, right_field, result_field, operation, blank_is_zero
        )
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def is_conditional(cls):
        return True

    @classmethod
    def get_task_type_string(cls):
        return K_ARITHMETIC

    def __init__(self, name, when, resulting_fields, left_field, right_field, result_field, operation, blank_is_zero):
        super(ArithmeticTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.left_field = left_field
        self.right_field = right_field
        self.result_field = result_field
        self.operation = operation
        self.blank_is_zero = blank_is_zero

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when,
            self.resulting_fields == other.resulting_fields,
            self.left_field == other.left_field,
            self.right_field == other.right_field,
            self.result_field == other.result_field,
            self.operation == other.operation,
            self.blank_is_zero == other.blank_is_zero
        ])

    def __str__(self):
        return "ArithmeticTask(%s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.left_field, self.right_field, self.result_field,
            self.operation, self.blank_is_zero
        )

    def __repr__(self):
        return str(self)

    def __compute(self, left_value, right_value, operation):
        if operation == E_ADD:
            retval = left_value + right_value
        elif operation == E_SUBTRACT:
            retval = left_value - right_value
        elif operation == E_MULTIPLY:
            retval = left_value * right_value
        else:
            if right_value == 0:
                raise TransformationException(
                    'Cannot divide by zero (value of field "%s" is zero).' % self.right_field
                )
            retval = left_value / right_value
        return str(retval)

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        _check_field_existence(rowdict, [self.left_field, self.right_field, self.result_field])
        left_value = _get_numerical_value(rowdict, self.left_field, self.blank_is_zero)
        right_value = _get_numerical_value(rowdict, self.right_field, self.blank_is_zero)
        result = self.__compute(left_value, right_value, self.operation)
        output[self.result_field] = result
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
