import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.config.classes import Fileset, InputFile, Sheet, TaskParsingContext, YamlPathContext
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.CsvMatchTask import K_CSV_MATCH, K_DIRECTORY, K_FILENAME_REGEX, K_LOOKUP_COLUMN, K_FIELDS, \
    K_MATCH_VALUE, K_UNMATCH_VALUE
from dataunifier.tasks import CsvMatchTask
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest
from tests.constants import TESTASSETS_DIR, TESTCSV_NAME, TESTCSV_DUP_NAME, TESTCSV_PATH


class TestCsvMatchTask(unittest.TestCase):
    def test_create_from_config_success(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "%INPUT_DIR%",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_MATCH_VALUE: "match",
            K_UNMATCH_VALUE: "unmatch"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_MATCH,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"lookup1", "lookup2"},
            "match", "unmatch"
        )
        output1 = CsvMatchTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_nonexistent_dir(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "nonexistent",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_MATCH_VALUE: "match",
            K_UNMATCH_VALUE: "unmatch"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_MATCH,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvMatchTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Directory "%s" was specified in %s task "%s" but could not be found. (File "%s")' % (
                "nonexistent", K_CSV_MATCH, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_no_file(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^nonexistent\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_MATCH_VALUE: "match",
            K_UNMATCH_VALUE: "unmatch"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_MATCH,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvMatchTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find any files matching pattern "%s" for %s task "%s". (File "%s")' % (
                "^nonexistent\\.csv$", K_CSV_MATCH, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_duplicate_file(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv.*\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_MATCH_VALUE: "match",
            K_UNMATCH_VALUE: "unmatch"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_MATCH,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvMatchTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Found multiple files matching pattern "%s" for %s task "%s": "%s" (File "%s")' % (
                "^testcsv.*\\.csv$", K_CSV_MATCH, "taskName", '", "'.join([TESTCSV_NAME, TESTCSV_DUP_NAME]),
                "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_column(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "nonexistent",
            K_MATCH_VALUE: "match",
            K_UNMATCH_VALUE: "unmatch"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_MATCH,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvMatchTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'File "%s" does not contain lookup column "%s", required by %s task %s. (File "%s")' % (
                TESTCSV_PATH, "nonexistent", K_CSV_MATCH, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_CSV_MATCH
        output1 = CsvMatchTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = CsvMatchTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = CsvMatchTask(
            "taskName1", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName2", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field3"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field2"], {"value1", "value2"},
            "match", "unmatch"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_lookup_set(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value3"},
            "match", "unmatch"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_match_value(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match1", "unmatch"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match2", "unmatch"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_unmatch_value(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch1"
        )
        obj2 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch2"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = CsvMatchTask(
            "taskName", None, ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
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
                            TestFieldCreatorTask("task1", ["field1", "field2"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value1"}
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
                            TestFieldCreatorTask("task1", ["field1", "field2"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "match", "field2": "value1"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
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
                            TestFieldCreatorTask("task1", ["field1", "field2"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value1"}
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
                            TestFieldCreatorTask("task1", ["field1", "field2"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "match", "field2": "value1"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
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
                            TestFieldCreatorTask("task1", ["field1", "field2"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field1": "value1", "field2": "value1"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch"
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
                            TestFieldCreatorTask("task1", ["field1", "field2"])
                        )
                    ),
                    InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
                ),
                "filepath", "sheet", ["row1", "row2"]
            ), 1, {"field3": "value1", "field2": "value1"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field1"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = CsvMatchTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"value1", "value2"},
            "match", "unmatch1"
        )
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
