import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.config.classes import Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when import Or
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestOr(unittest.TestCase):
    def test_eq(self):
        obj1 = Or([WhenSimpleTest("true"), WhenSimpleTest("true")])
        obj2 = Or([WhenSimpleTest("true"), WhenSimpleTest("true")])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne(self):
        obj1 = Or([WhenSimpleTest("true"), WhenSimpleTest("true1")])
        obj2 = Or([WhenSimpleTest("true"), WhenSimpleTest("true2")])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_evaluate_true(self):
        obj1 = Or([WhenSimpleTest(), WhenSimpleTest("true")])
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
            ), 1, {"field1": "value1"}
        )
        output1 = obj1.evaluate(input1)
        self.assertTrue(output1)

    def test_evaluate_false(self):
        obj1 = Or([WhenSimpleTest(), WhenSimpleTest()])
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
            ), 1, {"field1": "value1"}
        )
        output1 = obj1.evaluate(input1)
        self.assertFalse(output1)
