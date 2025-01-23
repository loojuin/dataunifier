import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import DiscardRecordException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.DiscardRecordTask import K_DISCARD_RECORD, DiscardRecordTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestDiscardRecordTask(unittest.TestCase):
    def test_create_from_config(self):
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", {}
            ),
            "taskName",
            K_DISCARD_RECORD,
            WhenSimpleTest("True"),
            TestFieldCreatorTask("taskName", ["field1", "field2"])
        )
        correct1 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field2"])
        output1 = DiscardRecordTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_DISCARD_RECORD
        output1 = DiscardRecordTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = DiscardRecordTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field2"])
        obj2 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field2"])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = DiscardRecordTask("taskName1", WhenSimpleTest("True"), ["field1", "field2"])
        obj2 = DiscardRecordTask("taskName2", WhenSimpleTest("True"), ["field1", "field2"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = DiscardRecordTask("taskName", WhenSimpleTest("True1"), ["field1", "field2"])
        obj2 = DiscardRecordTask("taskName", WhenSimpleTest("True2"), ["field1", "field2"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field2"])
        obj2 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field3"])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_false(self):
        obj1 = DiscardRecordTask("taskName", WhenSimpleTest(), ["field1", "field2"])
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
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field2"])
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
        except DiscardRecordException:
            pass

    def test_transform_when_none(self):
        obj1 = DiscardRecordTask("taskName", None, ["field1", "field2"])
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
        except DiscardRecordException:
            pass

    def test_get_resulting_fields(self):
        obj1 = DiscardRecordTask("taskName", WhenSimpleTest("True"), ["field1", "field2"])
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
