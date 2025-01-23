import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.config.classes import Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import SetFieldValueTask, UppercaseTask
from dataunifier.tasks.BlockTask import K_BLOCK, BlockTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestBlockClass(unittest.TestCase):
    def test_get_task_type_string(self):
        correct1 = K_BLOCK
        output1 = BlockTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = BlockTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = BlockTask(
            "taskName",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        obj2 = BlockTask(
            "taskName",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = BlockTask(
            "taskName1",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        obj2 = BlockTask(
            "taskName2",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = BlockTask(
            "taskName",
            WhenSimpleTest("when1"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        obj2 = BlockTask(
            "taskName",
            WhenSimpleTest("when2"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_task_list(self):
        obj1 = BlockTask(
            "taskName",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        obj2 = BlockTask(
            "taskName",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName3", ["field3", "field4"])
            ]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = BlockTask(
            "taskName",
            None,
            [
                SetFieldValueTask("setFieldValueTask", None, ["field1"], "field1", "MakeMeUpperCase"),
                UppercaseTask("uppercaseTask", None, ["field1"], ["field1"])
            ]
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
            ), 1, {"field1": ""}
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
            ), 1, {"field1": "MAKEMEUPPERCASE"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = BlockTask(
            "taskName",
            WhenSimpleTest("true"),
            [
                SetFieldValueTask("setFieldValueTask", None, ["field1"], "field1", "MakeMeUpperCase"),
                UppercaseTask("uppercaseTask", None, ["field1"], ["field1"])
            ]
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
            ), 1, {"field1": ""}
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
            ), 1, {"field1": "MAKEMEUPPERCASE"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = BlockTask(
            "taskName",
            WhenSimpleTest(),
            [
                SetFieldValueTask("setFieldValueTask", None, ["field1"], "field1", "MakeMeUpperCase"),
                UppercaseTask("uppercaseTask", None, ["field1"], ["field1"])
            ]
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
            ), 1, {"field1": ""}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = BlockTask(
            "taskName1",
            WhenSimpleTest("when"),
            [
                TestFieldCreatorTask("innerTaskName1", ["field1", "field2"]),
                TestFieldCreatorTask("innerTaskName2", ["field3", "field4"])
            ]
        )
        correct1 = ["field3", "field4"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
