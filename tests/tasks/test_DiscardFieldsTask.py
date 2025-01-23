import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.DiscardFieldsTask import K_FIELDS, K_DISCARD_FIELDS, DiscardFieldsTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestDiscardFieldsTask(unittest.TestCase):
    def test_create_from_config_success(self):
        config_dict = {
            K_FIELDS: [
                "field1", "field2"
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName", K_DISCARD_FIELDS, None, TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        correct1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        output1 = DiscardFieldsTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_when_not_none(self):
        config_dict = {
            K_FIELDS: [
                "field1", "field2"
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName", K_DISCARD_FIELDS, WhenSimpleTest(),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        try:
            DiscardFieldsTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = '"when" cannot be used with a %s task. (File "%s", task "%s")' % (
                K_DISCARD_FIELDS, "currentFile", "taskName"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_DISCARD_FIELDS
        output1 = DiscardFieldsTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = False
        output1 = DiscardFieldsTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        obj2 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = DiscardFieldsTask("taskName1", ["field1", "field2", "field3"], ["field1", "field2"])
        obj2 = DiscardFieldsTask("taskName2", ["field1", "field2", "field3"], ["field1", "field2"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_eq_diff_when(self):
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        obj2 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_previous_task_fields(self):
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        obj2 = DiscardFieldsTask("taskName", ["field1", "field2", "field4"], ["field1", "field2"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_field_list(self):
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field2"])
        obj2 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field1", "field3"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform(self):
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
            ), 1, {"field1": "value1", "field2": "value2", "field3": "value3"}
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
            ), 1, {"field1": "value1", "field3": "value3"}
        )
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field2"])
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_with_when(self):
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
            ), 1, {"field1": "value1", "field2": "value2", "field3": "value3"}
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
            ), 1, {"field1": "value1", "field3": "value3"}
        )
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field2"])
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = DiscardFieldsTask("taskName", ["field1", "field2", "field3"], ["field2", "field4"])
        correct1 = ["field1", "field3"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
