import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.ConcatenateFieldsTask import K_FIELDS, K_TO_FIELD, K_WITH_STRING, K_CONCATENATE_FIELDS, \
    ConcatenateFieldsTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestConcatenateFieldsTask(unittest.TestCase):
    def test_create_from_config_success(self):
        config_dict = {
            K_FIELDS: ["field1", "field2"],
            K_TO_FIELD: "field3",
            K_WITH_STRING: "_"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName", K_CONCATENATE_FIELDS, WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        correct1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        output1 = ConcatenateFieldsTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_fields(self):
        config_dict = {
            K_FIELDS: ["field1", "field4"],
            K_TO_FIELD: "field3",
            K_WITH_STRING: "_"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName", K_CONCATENATE_FIELDS, WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        try:
            ConcatenateFieldsTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" was expected by %s task "%s", but was not found in resulting fields ' \
                       'from preceding %s task "%s". (File "%s")' % (
                           "field4", K_CONCATENATE_FIELDS, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_CONCATENATE_FIELDS
        output1 = ConcatenateFieldsTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = ConcatenateFieldsTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = ConcatenateFieldsTask(
            "taskName1", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName2", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field4"], ["field1", "field2"],
            "field3", "_"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field3"],
            "field3", "_"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_to_field(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field4", "_"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_with_string(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
        )
        obj2 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "-"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", None, ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "replaceMe"}
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "cat1_cat2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "replaceMe"}
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "cat1_cat2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", WhenSimpleTest(), ["field1", "field2", "field3"], ["field1", "field2"],
            "field3", "_"
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "replaceMe"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_fields(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", None, ["field1", "field2", "field3"], ["field4", "field2"],
            "field3", "_"
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s"' % "field4"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_missing_to_fields(self):
        obj1 = ConcatenateFieldsTask(
            "taskName", None, ["field1", "field2", "field3"], ["field1", "field2"],
            "field4", "_"
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
            ), 1, {"field1": "cat1", "field2": "cat2", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s"' % "field4"
            output1 = e.message
            self.assertEqual(correct1, output1)
