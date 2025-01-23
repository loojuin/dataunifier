import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.config.classes import Fileset, InputFile, Sheet, TaskParsingContext, YamlPathContext
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import CsvLookupReplaceTask
from dataunifier.tasks.CsvLookupReplaceTask import K_CSV_LOOKUP_REPLACE, E_FAIL, E_PASSTHROUGH, E_BLANK, K_FIELDS, \
    K_DIRECTORY, K_FILENAME_REGEX, K_LOOKUP_COLUMN, K_VALUE_COLUMN, K_ON_UNMATCHED, K_DEDUPLICATE_BY, \
    E_LOWER_ROW_NUMBER, E_HIGHER_ROW_NUMBER
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest
from tests.constants import TESTASSETS_DIR, TESTCSV_NAME, TESTCSV_DUP_NAME, TESTCSV_DUP_PATH, TESTCSV_PATH


class TestCsvLookupReplaceTask(unittest.TestCase):
    def test_create_from_config_success(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "%INPUT_DIR%",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"],
            {"lookup1": "value1", "lookup2": "value2"}, E_FAIL
        )
        output1 = CsvLookupReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_success_with_deduplicate_by(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "%INPUT_DIR%",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL,
            K_DEDUPLICATE_BY: E_LOWER_ROW_NUMBER
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        correct1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"],
            {"lookup1": "value1", "lookup2": "value2"}, E_FAIL
        )
        output1 = CsvLookupReplaceTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_nonexistent_dir(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "nonexistent",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Directory "%s" was specified in %s task "%s" but could not be found. (File "%s")' % (
                "nonexistent", K_CSV_LOOKUP_REPLACE, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_no_file(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^nonexistent\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find any files matching pattern "%s" for %s task "%s". (File "%s")' % (
                "^nonexistent\\.csv$", K_CSV_LOOKUP_REPLACE, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_duplicate_file(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv.*\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Found multiple files matching pattern "%s" for %s task "%s": "%s" (File "%s")' % (
                "^testcsv.*\\.csv$", K_CSV_LOOKUP_REPLACE, "taskName",
                '", "'.join([TESTCSV_NAME, TESTCSV_DUP_NAME]), "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_duplicate_value_no_deduplicate_by(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv_dup\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Duplicate value "%s" found in lookup column "%s" of file "%s", when preparing %s ' \
                       'task "%s" (File "%s")' % (
                           "lookup1", "lookup", TESTCSV_DUP_PATH, K_CSV_LOOKUP_REPLACE, "taskName", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_duplicate_value_deduplicate_by_lower_row_number(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv_dup\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL,
            K_DEDUPLICATE_BY: E_LOWER_ROW_NUMBER
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        task = CsvLookupReplaceTask.create_from_config(input1)
        correct1 = "value1"
        output1 = task.lookup_dict["lookup1"]
        self.assertEqual(correct1, output1)

    def test_create_from_config_duplicate_value_deduplicate_by_higher_row_number(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv_dup\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL,
            K_DEDUPLICATE_BY: E_HIGHER_ROW_NUMBER
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        task = CsvLookupReplaceTask.create_from_config(input1)
        correct1 = "value3"
        output1 = task.lookup_dict["lookup1"]
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_lookup_col(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "nonexistent",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'File "%s" does not contain column "%s", required by %s task %s. (File "%s")' % (
                TESTCSV_PATH, "nonexistent", K_CSV_LOOKUP_REPLACE, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_value_col(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: TESTASSETS_DIR,
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "nonexistent",
            K_ON_UNMATCHED: E_FAIL
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'File "%s" does not contain column "%s", required by %s task %s. (File "%s")' % (
                TESTCSV_PATH, "nonexistent", K_CSV_LOOKUP_REPLACE, "taskName", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_on_unmatched(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "%INPUT_DIR%",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: "invalid"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                f"current.key.{K_ON_UNMATCHED}", "invalid",
                '", "'.join([E_FAIL, E_BLANK, E_PASSTHROUGH]), "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_deduplicate_by(self):
        config_dict = {
            K_FIELDS: ["field1"],
            K_DIRECTORY: "%INPUT_DIR%",
            K_FILENAME_REGEX: "^testcsv\\.csv$",
            K_LOOKUP_COLUMN: "lookup",
            K_VALUE_COLUMN: "value",
            K_ON_UNMATCHED: E_FAIL,
            K_DEDUPLICATE_BY: "invalid"
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_CSV_LOOKUP_REPLACE,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2"])
        )
        try:
            CsvLookupReplaceTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                f"current.key.{K_DEDUPLICATE_BY}", "invalid",
                '", "'.join([E_HIGHER_ROW_NUMBER, E_LOWER_ROW_NUMBER]), "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_CSV_LOOKUP_REPLACE
        output1 = CsvLookupReplaceTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = CsvLookupReplaceTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = CsvLookupReplaceTask(
            "taskName1", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName2", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field3"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_field(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field2"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_lookup_dict(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b3"},
            E_FAIL
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_on_unmatched(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        obj2 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_PASSTHROUGH
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask("taskName", None, ["field1", "field2"], ["field1"], lookup_dict, E_FAIL)
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
            ), 1, {"field1": "a1", "field2": "a2"}
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
            ), 1, {"field1": "b1", "field2": "a2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], lookup_dict, E_FAIL
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
            ), 1, {"field1": "a1", "field2": "a2"}
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
            ), 1, {"field1": "b1", "field2": "a2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest(), ["field1", "field2"], ["field1"], lookup_dict, E_FAIL
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
            ), 1, {"field1": "a1", "field2": "a2"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask(
            "taskName", None, ["field1", "field2"], ["field1"], lookup_dict, E_FAIL
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
            ), 1, {"field3": "a1", "field2": "a2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field1"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_unmatched_passthrough(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], lookup_dict, E_PASSTHROUGH
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
            ), 1, {"field1": "a3", "field2": "a2"}
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
            ), 1, {"field1": "a3", "field2": "a2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_unmatched_blank(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], lookup_dict, E_BLANK
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
            ), 1, {"field1": "a3", "field2": "a2"}
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
            ), 1, {"field1": "", "field2": "a2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_unmatched_fail(self):
        lookup_dict = {"a1": "b1", "a2": "b2"}
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2"], ["field1"], lookup_dict, E_FAIL
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
            ), 1, {"field1": "a3", "field2": "a2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Encountered unrecognised value in field "%s": "%s"' % (
                "field1", "a3"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = CsvLookupReplaceTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2"], ["field1"], {"a1": "b1", "a2": "b2"},
            E_FAIL
        )
        correct1 = ["field1", "field2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
