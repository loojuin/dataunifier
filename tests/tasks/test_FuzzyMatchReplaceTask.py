import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.config.classes import Fileset, InputFile, Sheet, TaskParsingContext, YamlPathContext
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.FuzzyMatchReplaceTask import JaccardRule, K_FUZZY_MATCH_REPLACE, E_JACCARD, E_FAIL, E_BLANK, \
    E_PASSTHROUGH, K_FIELDS, K_METHOD, K_RULES, K_STRING, K_REPLACEMENT, K_MINIMUM_SCORE, K_ON_UNMATCHED, \
    DEFAULT_NGRAM_SIZE, K_NGRAM_SIZE
from dataunifier.tasks import FuzzyMatchReplaceTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestJaccardRule(unittest.TestCase):
    def test_eq(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        obj2 = JaccardRule("string1", "replacement1", 3)
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_string(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        obj2 = JaccardRule("string2", "replacement1", 3)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_replacement(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        obj2 = JaccardRule("string1", "replacement2", 3)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_ngram_size(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        obj2 = JaccardRule("string1", "replacement2", 3)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ngramify_undersized(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        input1 = "te"
        correct1 = {"te"}
        output1 = obj1.ngramify(input1)
        self.assertEqual(correct1, output1)

    def test_ngramify_normal(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        input1 = "string1"
        correct1 = {"str", "tri", "rin", "ing", "ng1"}
        output1= obj1.ngramify(input1)
        self.assertEqual(correct1, output1)

    def test_evaluate_100_percent(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        input1 = "string1"
        correct1 = 1.0
        output1 = obj1.evaluate(input1)
        self.assertEqual(correct1, output1)

    def test_evaluate_0_percent(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        input1 = "1gnirts"
        correct1 = 0.0
        output1 = obj1.evaluate(input1)
        self.assertEqual(correct1, output1)

    def test_evaluate_50_percent(self):
        obj1 = JaccardRule("string1", "replacement1", 3)
        input1 = "string123456"
        correct1 = 0.5
        output1 = obj1.evaluate(input1)
        self.assertEqual(correct1, output1)


class TestFuzzyMatchReplaceTask(unittest.TestCase):
    def test_create_from_config(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_METHOD: E_JACCARD,
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], E_JACCARD,
            [
                JaccardRule("string1a", "replacement1", DEFAULT_NGRAM_SIZE),
                JaccardRule("string1b", "replacement1", DEFAULT_NGRAM_SIZE),
                JaccardRule("string2", "replacement2", DEFAULT_NGRAM_SIZE)
            ],
            0.5,
            E_FAIL
        )
        output1 = FuzzyMatchReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_method(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], E_JACCARD,
            [
                JaccardRule("string1a", "replacement1", DEFAULT_NGRAM_SIZE),
                JaccardRule("string1b", "replacement1", DEFAULT_NGRAM_SIZE),
                JaccardRule("string2", "replacement2", DEFAULT_NGRAM_SIZE)
            ],
            0.5,
            E_FAIL
        )
        output1 = FuzzyMatchReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_with_ngram_size(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL,
            K_NGRAM_SIZE: 2
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], E_JACCARD,
            [
                JaccardRule("string1a", "replacement1", 2),
                JaccardRule("string1b", "replacement1", 2),
                JaccardRule("string2", "replacement2", 2)
            ],
            0.5,
            E_FAIL
        )
        output1 = FuzzyMatchReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_ngram_size_string(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL,
            K_NGRAM_SIZE: "notANumber"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            FuzzyMatchReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid %s: "%s". Must be an integer more than 0. (File "%s", Task "%s")' % (
                K_NGRAM_SIZE, "notANumber", "currentFile", "taskName"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_ngram_size_invalid(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL,
            K_NGRAM_SIZE: "0"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            FuzzyMatchReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid %s: "%s". Must be an integer more than 0. (File "%s", Task "%s")' % (
                K_NGRAM_SIZE, "0", "currentFile", "taskName"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_method(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_METHOD: "invalidMethod",
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            FuzzyMatchReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                "current.key.%s" % K_METHOD, "invalidMethod", '", "'.join([E_JACCARD]), "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_on_unmatched(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_METHOD: E_JACCARD,
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: "invalidOnUnmatched"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            FuzzyMatchReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                "current.key.%s" % K_ON_UNMATCHED, "invalidOnUnmatched",
                '", "'.join([E_FAIL, E_BLANK, E_PASSTHROUGH]), "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        config_dict = {
            K_FIELDS: ["field3"],
            K_METHOD: E_JACCARD,
            K_RULES: [
                {K_STRING: ["string1a", "string1b"], K_REPLACEMENT: "replacement1"},
                {K_STRING: "string2", K_REPLACEMENT: "replacement2"}
            ],
            K_MINIMUM_SCORE: 0.5,
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_FUZZY_MATCH_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            FuzzyMatchReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       '%s task "%s". (File "%s")' % (
                           "field3", K_FUZZY_MATCH_REPLACE, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_FUZZY_MATCH_REPLACE
        output1 = FuzzyMatchReplaceTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = FuzzyMatchReplaceTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName1", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName2", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field3"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field3"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_method(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], "test",
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_rules(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string2", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_minimum_score(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.6, E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_on_unmatched(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        obj2 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1", "field2"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_BLANK
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", None, ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
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
            ), 1, {"field1": "ring2", "field2": "ring2"}
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
            ), 1, {"field1": "replacement2", "field2": "ring2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
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
            ), 1, {"field1": "ring2", "field2": "ring2"}
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
            ), 1, {"field1": "replacement2", "field2": "ring2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
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
            ), 1, {"field1": "ring2", "field2": "ring2"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", None, ["field1", "field2"], ["field3"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
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
            ), 1, {"field1": "ring2", "field2": "ring2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field3"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_unmatched_blank(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", None, ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_BLANK
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
            ), 1, {"field1": "xxxxxxxxxxxng2", "field2": "xxxxxxxxxxxng2"}
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
            ), 1, {"field1": "", "field2": "xxxxxxxxxxxng2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_unmatched_passthrough(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", None, ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5,
            E_PASSTHROUGH
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
            ), 1, {"field1": "xxxxxxxxxxxng2", "field2": "xxxxxxxxxxxng2"}
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
            ), 1, {"field1": "xxxxxxxxxxxng2", "field2": "xxxxxxxxxxxng2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_unmatched_fail(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", None, ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
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
            ), 1, {"field1": "xxxxxxxxxxxng2", "field2": "xxxxxxxxxxxng2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not match value "%s" in field "%s" to any rules.' % ("xxxxxxxxxxxng2", "field1")
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = FuzzyMatchReplaceTask(
            "taskName", None, ["field1", "field2"], ["field1"], E_JACCARD,
            [JaccardRule("string1", "replacement1", 3), JaccardRule("string2", "replacement2", 3)], 0.5, E_FAIL
        )
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
