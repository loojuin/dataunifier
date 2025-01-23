import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import UppercaseTask
from dataunifier.tasks.UppercaseTask import K_UPPERCASE, K_FIELDS
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestUppercaseTask(unittest.TestCase):
    def test_create_from_config_previous_task_none(self):
        config_dict = {
            K_FIELDS: ["field1", "field2"]
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_UPPERCASE, WhenSimpleTest("when"), None
        )
        correct1 = UppercaseTask("taskName", WhenSimpleTest("when"), None, ["field1", "field2"])
        output1 = UppercaseTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_with_previous_task(self):
        config_dict = {
            K_FIELDS: ["field1", "field2"]
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_UPPERCASE, WhenSimpleTest("when"), TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"])
        output1 = UppercaseTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        config_dict = {
            K_FIELDS: ["field1", "field2"]
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_UPPERCASE, WhenSimpleTest("when"), TestFieldCreatorTask("prevTask", ["field1"])
        )
        try:
            UppercaseTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       '%s task "%s". (File "%s")' % (
                           "field2", K_UPPERCASE, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_UPPERCASE
        output1 = UppercaseTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = UppercaseTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        obj2 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = UppercaseTask("taskName1", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        obj2 = UppercaseTask("taskName2", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = UppercaseTask("taskName", WhenSimpleTest("when1"), ["field1", "field2"], ["field1"])
        obj2 = UppercaseTask("taskName", WhenSimpleTest("when2"), ["field1", "field2"], ["field1"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        obj2 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field3"], ["field1"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        obj2 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field2"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_success(self):
        obj1 = UppercaseTask("taskName", None, ["field1", "field2", "field3"], ["field1", "field3"])
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
            ), 1, {"field1": "HiRe mE", "field2": "don't hire me", "field3": "hire me too"}
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
            ), 1, {"field1": "HIRE ME", "field2": "don't hire me", "field3": "HIRE ME TOO"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = UppercaseTask("taskName", None, ["field1", "field2", "field3"], ["field1", "field3"])
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
            ), 1, {"field1": "HiRe mE", "field2": "don't hire me"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field3"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = UppercaseTask("taskName", WhenSimpleTest(), ["field1", "field2", "field3"], ["field1", "field3"])
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
            ), 1, {"field1": "HiRe mE", "field2": "don't hire me", "field3": "hire me too"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = UppercaseTask("taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"])
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
