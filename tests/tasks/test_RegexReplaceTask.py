import re
import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import RegexReplaceTask
from dataunifier.tasks.RegexReplaceTask import RegexReplaceRule, K_REGEX_REPLACE, E_FAIL, E_PASSTHROUGH, K_FIELDS, \
    K_ON_UNMATCHED, K_ALLOW_BLANK, K_RULES, K_REPLACE, K_WITH, E_BLANK
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestRegexReplaceRule(unittest.TestCase):
    def test_eq(self):
        obj1 = RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
        obj2 = RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_regex_list(self):
        obj1 = RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
        obj2 = RegexReplaceRule([re.compile("regex1"), re.compile("regex3")], "replacement")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_replacement(self):
        obj1 = RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement1")
        obj2 = RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement2")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestRegexReplaceTask(unittest.TestCase):
    def test_create_from_config_full(self):
        value = {
            K_FIELDS: ["field1"],
            K_ON_UNMATCHED: E_FAIL,
            K_ALLOW_BLANK: True,
            K_RULES: [
                {K_REPLACE: ["regex1a", "regex1b"], K_WITH: "replacement1"},
                {K_REPLACE: ["regex2a", "regex2b"], K_WITH: "replacement2"}
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", value
            ),
            "taskName", K_REGEX_REPLACE, WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = RegexReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1a"), re.compile("regex1b")], "replacement1"),
                RegexReplaceRule([re.compile("regex2a"), re.compile("regex2b")], "replacement2")
            ],
            "currentFile"
        )
        output1 = RegexReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_on_unmatched(self):
        value = {
            K_FIELDS: ["field1"],
            K_ON_UNMATCHED: "matchit",
            K_ALLOW_BLANK: True,
            K_RULES: [
                {K_REPLACE: ["regex1a", "regex1b"], K_WITH: "replacement1"},
                {K_REPLACE: ["regex2a", "regex2b"], K_WITH: "replacement2"}
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", value
            ),
            "taskName", K_REGEX_REPLACE, WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            RegexReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                "current.key.%s" % K_ON_UNMATCHED, "matchit", '", "'.join([E_FAIL, E_BLANK, E_PASSTHROUGH]),
                "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        value = {
            K_FIELDS: ["field1"],
            K_ON_UNMATCHED: E_PASSTHROUGH,
            K_ALLOW_BLANK: True,
            K_RULES: [
                {K_REPLACE: ["regex1a", "regex1b"], K_WITH: "replacement1"},
                {K_REPLACE: ["regex2a", "regex2b"], K_WITH: "replacement2"}
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", value
            ),
            "taskName", K_REGEX_REPLACE, WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field2", "field3"])
        )
        try:
            RegexReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       '%s task "%s". (File "%s")' % (
                           "field1", K_REGEX_REPLACE, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_regex(self):
        value = {
            K_FIELDS: ["field1"],
            K_ON_UNMATCHED: E_PASSTHROUGH,
            K_ALLOW_BLANK: True,
            K_RULES: [
                {K_REPLACE: ["regex1a", "regex1b("], K_WITH: "replacement1"},
                {K_REPLACE: ["regex2a", "regex2b"], K_WITH: "replacement2"}
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", value
            ),
            "taskName", K_REGEX_REPLACE, WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field2", "field3"])
        )
        try:
            RegexReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid regular expression at key "%s": "%s". Details: "' % (
                f"current.key.{K_RULES}.0.{K_REPLACE}.1", "regex1b("
            )
            output1 = e.message
            self.assertEqual(correct1, output1[0:len(correct1)])

    def test_get_task_type_string(self):
        correct1 = K_REGEX_REPLACE
        output1 = RegexReplaceTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = RegexReplaceTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = RegexReplaceTask(
            "taskName1", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName2", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field3"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field2"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_on_unmatched(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_PASSTHROUGH, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_allow_blank(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, False, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_rules(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement1")
            ],
            "rulesFile"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement2")
            ],
            "rulesFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_rules_file(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement1")
            ],
            "rulesFile1"
        )
        obj2 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [
                RegexReplaceRule([re.compile("regex1"), re.compile("regex2")], "replacement1")
            ],
            "rulesFile2"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_success_when_none(self):
        obj1 = RegexReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field1": "I like chocolate", "field2": "I like bananas"}
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
            ), 1, {"field1": "chocolate is awesome", "field2": "I like bananas"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = RegexReplaceTask(
            "taskName",
            WhenSimpleTest(),
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field1": "I like chocolate", "field2": "I like bananas"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_on_unmatched_blank(self):
        obj1 = RegexReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_BLANK,
            False,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field1": "Nicht in haus", "field2": "I like bananas"}
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
            ), 1, {"field1": "", "field2": "I like bananas"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_on_unmatched_passthrough(self):
        obj1 = RegexReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_PASSTHROUGH,
            False,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field1": "Nicht in haus", "field2": "I like bananas"}
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
            ), 1, {"field1": "Nicht in haus", "field2": "I like bananas"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_on_unmatched_fail(self):
        obj1 = RegexReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field1": "", "field2": "I like bananas"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Encountered unrecognised value in field "%s": "%s". (Rules in file "%s")' % (
                "field1", "", "rulesFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_allow_blank(self):
        obj1 = RegexReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            True,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field1": "", "field2": "I like bananas"}
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
            ), 1, {"field1": "", "field2": "I like bananas"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = RegexReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            True,
            [
                RegexReplaceRule([re.compile("^.+key$")], "monkey"),
                RegexReplaceRule([re.compile("^I like (.+)$")], "\\1 is awesome")
            ],
            "rulesFile"
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
            ), 1, {"field3": "I like chocolate", "field2": "I like bananas"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field1"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = RegexReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_FAIL, True, [], "rulesFile"
        )
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
