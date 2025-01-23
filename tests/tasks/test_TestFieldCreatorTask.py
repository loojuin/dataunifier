import unittest

from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask


class TestTestFieldCreatorTask(unittest.TestCase):
    def test_init(self):
        fields = ["field1", "field2"]
        obj1 = TestFieldCreatorTask("prevTask", fields)
        correct1 = fields
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
