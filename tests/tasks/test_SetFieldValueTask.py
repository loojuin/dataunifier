import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import YamlPathContext, TaskParsingContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import SetFieldValueTask
from dataunifier.tasks.SetFieldValueTask import K_SET_FIELD_VALUE, K_FIELD, K_VALUE
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestSetFieldValueTask(unittest.TestCase):
    def test_get_task_type_string(self):
        correct1 = K_SET_FIELD_VALUE
        output1 = SetFieldValueTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = SetFieldValueTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_create_from_config_previous_task_none(self):
        config_dict = {
            K_FIELD: "field1",
            K_VALUE: "value1"
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", K_SET_FIELD_VALUE, config_dict),
            "taskName", K_SET_FIELD_VALUE, WhenSimpleTest(), None
        )
        correct1 = SetFieldValueTask("taskName", WhenSimpleTest(), None, "field1", "value1")
        output1 = SetFieldValueTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_with_previous_task(self):
        config_dict = {
            K_FIELD: "field1",
            K_VALUE: "value1"
        }
        previous_task = TestFieldCreatorTask("prevTask", ["field1", "field2"])
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", K_SET_FIELD_VALUE, config_dict),
            "taskName", K_SET_FIELD_VALUE, WhenSimpleTest(), previous_task
        )
        correct1 = SetFieldValueTask("taskName", WhenSimpleTest(), ["field1", "field2"], "field1", "value1")
        output1 = SetFieldValueTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        config_dict = {
            K_FIELD: "field1",
            K_VALUE: "value1"
        }
        previous_task = TestFieldCreatorTask("prevTask", ["field2"])
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", K_SET_FIELD_VALUE, config_dict),
            "taskName", K_SET_FIELD_VALUE, WhenSimpleTest(), previous_task
        )
        try:
            SetFieldValueTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s" but was not found in resulting fields from ' \
                       '%s task "%s". (File "%s")' % (
                           "field1", K_SET_FIELD_VALUE, "taskName",
                           previous_task.get_task_type_string(), previous_task.name, "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = SetFieldValueTask("taskName", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        obj2 = SetFieldValueTask("taskName", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        obj2 = SetFieldValueTask("taskName2", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = SetFieldValueTask("taskName", WhenSimpleTest("string1"), ["field1", "field2"], "field1", "value1")
        obj2 = SetFieldValueTask("taskName", WhenSimpleTest("string2"), ["field1", "field2"], "field1", "value1")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        obj2 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field3"], "field1", "value1")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_field(self):
        obj1 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        obj2 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field2"], "field2", "value1")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_value(self):
        obj1 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value1")
        obj2 = SetFieldValueTask("taskName1", WhenSimpleTest("string"), ["field1", "field2"], "field1", "value2")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_success(self):
        obj1 = SetFieldValueTask("taskName1", None, ["field1", "field2"], "field1", "newvalue")
        input1 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                        TestBogusDictWriter("writer1"),
                        Fileset(
                            "fileset1",
                            ["field1"],
                            [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                            TestFieldCreatorTask("task1", ["field1"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value2"}
        )
        correct1 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                        TestBogusDictWriter("writer1"),
                        Fileset(
                            "fileset1",
                            ["field1"],
                            [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                            TestFieldCreatorTask("task1", ["field1"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "newvalue", "field2": "value2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = SetFieldValueTask("taskName1", WhenSimpleTest(), ["field1", "field2"], "field1", "newvalue")
        input1 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                        TestBogusDictWriter("writer1"),
                        Fileset(
                            "fileset1",
                            ["field1"],
                            [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                            TestFieldCreatorTask("task1", ["field1"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value2"}
        )
        correct1 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                        TestBogusDictWriter("writer1"),
                        Fileset(
                            "fileset1",
                            ["field1"],
                            [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                            TestFieldCreatorTask("task1", ["field1"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = SetFieldValueTask("taskName1", None, ["field1", "field2"], "field3", "newvalue")
        input1 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                        TestBogusDictWriter("writer1"),
                        Fileset(
                            "fileset1",
                            ["field1"],
                            [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                            TestFieldCreatorTask("task1", ["field1"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field3"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = SetFieldValueTask("taskName", WhenSimpleTest("string1"), ["field1", "field2"], "field1", "value1")
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
