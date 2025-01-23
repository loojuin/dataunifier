import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.ReplaceTask import ReplaceRule, K_FIELDS, K_ON_UNMATCHED, E_FAIL, K_ALLOW_BLANK, K_RULES, \
    K_REPLACE, K_WITH, ReplaceTask, E_BLANK, E_PASSTHROUGH
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestReplaceRule(unittest.TestCase):
    def test_eq(self):
        obj1 = ReplaceRule(["string1", "string2"], "replacement1")
        obj2 = ReplaceRule(["string1", "string2"], "replacement1")
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_string_list(self):
        obj1 = ReplaceRule(["string1", "string2"], "replacement1")
        obj2 = ReplaceRule(["string1", "string3"], "replacement1")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_replacement(self):
        obj1 = ReplaceRule(["string1", "string2"], "replacement1")
        obj2 = ReplaceRule(["string1", "string2"], "replacement2")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestReplaceTask(unittest.TestCase):
    def test_create_from_config_success(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_ON_UNMATCHED: E_FAIL,
            K_ALLOW_BLANK: False,
            K_RULES: [
                {
                    K_REPLACE: ["string1a", "string1b"],
                    K_WITH: "replacement1"
                },
                {
                    K_REPLACE: "string2",
                    K_WITH: "replacement2"
                }
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputfilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_REPLACE,
            WhenSimpleTest("true"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        correct1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        output1 = ReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_on_unmatched(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_ON_UNMATCHED: "invalid",
            K_ALLOW_BLANK: False,
            K_RULES: [
                {
                    K_REPLACE: ["string1a", "string1b"],
                    K_WITH: "replacement1"
                },
                {
                    K_REPLACE: "string2",
                    K_WITH: "replacement2"
                }
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputfilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_REPLACE,
            WhenSimpleTest("true"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        try:
            ReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s" in task "%s": "%s". Accepted values are: "%s".' \
                       '(File "%s")' % (
                           K_ON_UNMATCHED, "taskName", "invalid", '", "'.join([E_BLANK, E_PASSTHROUGH, E_FAIL]),
                           "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        config_dict = {
            K_FIELDS: ["field4"],
            K_ON_UNMATCHED: E_FAIL,
            K_ALLOW_BLANK: False,
            K_RULES: [
                {
                    K_REPLACE: ["string1a", "string1b"],
                    K_WITH: "replacement1"
                },
                {
                    K_REPLACE: "string2",
                    K_WITH: "replacement2"
                }
            ]
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputfilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_REPLACE,
            WhenSimpleTest("true"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        try:
            ReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       '%s task "%s". (File "%s")' % (
                           "field4", K_REPLACE, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_REPLACE
        output1 = ReplaceTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = ReplaceTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = ReplaceTask(
            "taskName1",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName2",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true1"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true2"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field4"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field2"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_on_unmatched(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_BLANK,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_allow_blank(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            True,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_rules(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string3"], "replacement3")
            ],
            "currentFile"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_rules_file(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile1"
        )
        obj2 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2", "field3"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile2"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = ReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field1": "string1b", "field2": "string1b"}
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
            ), 1, {"field1": "replacement1", "field2": "string1b"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest("true"),
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field1": "string1b", "field2": "string1b"}
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
            ), 1, {"field1": "replacement1", "field2": "string1b"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = ReplaceTask(
            "taskName",
            WhenSimpleTest(),
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field1": "string1b", "field2": "string1b"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = ReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field4": "string1b", "field2": "string1b"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "field1".'
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_unmatched_passthrough(self):
        obj1 = ReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_PASSTHROUGH,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field1": "string3", "field2": "string3"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_unmatched_blank(self):
        obj1 = ReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_BLANK,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field1": "string3", "field2": "string3"}
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
            ), 1, {"field1": "", "field2": "string3"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_unmatched_fail(self):
        obj1 = ReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
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
            ), 1, {"field1": "string3", "field2": "string3"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Encountered unrecognised value in field "%s": "%s". (Rules in file "%s")' % (
                "field1", "string3", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = ReplaceTask(
            "taskName",
            None,
            ["field1", "field2"],
            ["field1"],
            E_FAIL,
            False,
            [
                ReplaceRule(["string1a", "string1b"], "replacement1"),
                ReplaceRule(["string2"], "replacement2")
            ],
            "currentFile"
        )
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
