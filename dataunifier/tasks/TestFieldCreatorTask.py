"""
TestFieldCreatorTask module.
"""

from dataunifier.common.exceptions import TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask


K_TEST_FIELD_CREATOR = "test_field_creator"


class TestFieldCreatorTask(AbstractRegularTask):
    """
    A test task that just produces a the resulting fields you want.

    For use in unit testing only.
    """

    TRANSFORMATION_EXCEPTION_MESSAGE = "THIS IS A TEST"

    @classmethod
    def create_from_config(cls, task_parsing_context):
        raise Exception("You are not supposed to use the TestFieldCreatorTask outside of testing...")

    @classmethod
    def get_task_type_string(cls):
        return K_TEST_FIELD_CREATOR

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, fields):
        self.fields = fields
        super(TestFieldCreatorTask, self).__init__(name, None)

    def transform(self, row_ctxt):
        raise TransformationException(self.TRANSFORMATION_EXCEPTION_MESSAGE)

    def get_resulting_fields(self):
        return self.fields
