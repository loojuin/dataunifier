import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import TransformationException
from dataunifier.config.classes import Fileset, InputFile, Sheet, WhenParsingContext, YamlPathContext
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when import WhenFieldMatchesRegex
from dataunifier.when.WhenFieldMatchesRegex import K_VALUE_OF_FIELD, K_MATCHES_REGEX


class TestWhenFieldMatchesRegex(unittest.TestCase):
    def test_create_from_config_single(self):
        config_dict = {
            K_VALUE_OF_FIELD: "field",
            K_MATCHES_REGEX: "regex"
        }
        input1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "rootFile", "root.key.path", 0
        )
        correct1 = WhenFieldMatchesRegex("field", ["regex"])
        output1 = WhenFieldMatchesRegex.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_list(self):
        config_dict = {
            K_VALUE_OF_FIELD: "field",
            K_MATCHES_REGEX: ["regex1", "regex2"]
        }
        input1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "rootFile", "root.key.path", 0
        )
        correct1 = WhenFieldMatchesRegex("field", ["regex1", "regex2"])
        output1 = WhenFieldMatchesRegex.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_evaluate_true(self):
        obj1 = WhenFieldMatchesRegex("field1", ["^match\\d{8}$"])
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
            ), 1, {"field1": "match12345678"}
        )
        output1 = obj1.evaluate(input1)
        self.assertTrue(output1)

    def test_evaluate_false(self):
        obj1 = WhenFieldMatchesRegex("field1", ["^match\\d{8}$", "^iveSeenYouBefore$"])
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
            ), 1, {"field1": "neverSeenBefore"}
        )
        output1 = obj1.evaluate(input1)
        self.assertFalse(output1)

    def test_evaluate_missing_field(self):
        obj1 = WhenFieldMatchesRegex("field1", ["^match\\d{8}$", "^iveSeenYouBefore$"])
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
            ), 1, {"field3": "neverSeenBefore"}
        )
        try:
            obj1.evaluate(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field1"
            output1 = e.message
            self.assertEqual(correct1, output1)
