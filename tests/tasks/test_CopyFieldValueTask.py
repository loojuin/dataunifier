import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.CopyFieldValueTask import K_FROM_FIELD, K_TO_FIELDS, K_COPY_FIELD_VALUE, CopyFieldValueTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestCopyFieldValueTask(unittest.TestCase):
    def test_create_from_config_success(self):
        value = {
            K_FROM_FIELD: "field1",
            K_TO_FIELDS: ["field2", "field3"]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", value
            ),
            "taskName",
            K_COPY_FIELD_VALUE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        correct1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        output1 = CopyFieldValueTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        value = {
            K_FROM_FIELD: "field1",
            K_TO_FIELDS: ["field2", "field3"]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", value
            ),
            "taskName",
            K_COPY_FIELD_VALUE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CopyFieldValueTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" was expected by %s task "%s", but was not found in resulting fields of ' \
                       'preceding %s task "%s". (File "%s")' % (
                           "field3", K_COPY_FIELD_VALUE, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_COPY_FIELD_VALUE
        output1 = CopyFieldValueTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = CopyFieldValueTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        obj2 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = CopyFieldValueTask(
            "taskName1", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        obj2 = CopyFieldValueTask(
            "taskName2", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        obj2 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        obj2 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field4"], "field1", ["field2", "field3"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_from_field(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        obj2 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field2", ["field2", "field3"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_to_fields(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        obj2 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field4"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = CopyFieldValueTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
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
            ), 1, {"field1": "copyMe", "field2": "replaceMe", "field3": "replaceMe"}
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
            ), 1, {"field1": "copyMe", "field2": "copyMe", "field3": "copyMe"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
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
            ), 1, {"field1": "copyMe", "field2": "replaceMe", "field3": "replaceMe"}
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
            ), 1, {"field1": "copyMe", "field2": "copyMe", "field3": "copyMe"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = CopyFieldValueTask(
            "taskName", WhenSimpleTest(), ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
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
            ), 1, {"field1": "copyMe", "field2": "replaceMe", "field3": "replaceMe"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_from_field(self):
        obj1 = CopyFieldValueTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
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
            ), 1, {"field4": "copyMe", "field2": "replaceMe", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field1"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_missing_to_fields(self):
        obj1 = CopyFieldValueTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
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
            ), 1, {"field1": "copyMe", "field2": "replaceMe", "field4": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field3"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = CopyFieldValueTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", ["field2", "field3"]
        )
        correct1 = ["field1", "field2", "field3"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
