import unittest

import dataunifier.common.constants as commonconstants

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import TaskParsingContext, YamlPathContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import ConvertDateFormatTask
from dataunifier.tasks.ConvertDateFormatTask import K_CONVERT_DATE_FORMAT, K_FIELDS, K_ACCEPTED_FORMATS, \
    K_TARGET_FORMAT, K_ALLOW_BLANK, K_TIMEZONE
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestConvertDateFormatTask(unittest.TestCase):
    def test_get_task_type_string(self):
        correct1 = K_CONVERT_DATE_FORMAT
        output1 = ConvertDateFormatTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = ConvertDateFormatTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_create_from_config_previous_task_none(self):
        config_dict = {
            K_FIELDS: ["field1", "field2", "field3"],
            K_ACCEPTED_FORMATS: ["format1", "format2", "format3"],
            K_TARGET_FORMAT: "targetFormat",
            K_ALLOW_BLANK: False
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_CONVERT_DATE_FORMAT, WhenSimpleTest(), None
        )
        correct1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest(),
            None,
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        output1 = ConvertDateFormatTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_with_previous_task(self):
        config_dict = {
            K_FIELDS: ["field1", "field2", "field3"],
            K_ACCEPTED_FORMATS: ["format1", "format2", "format3"],
            K_TARGET_FORMAT: "targetFormat",
            K_ALLOW_BLANK: False
        }
        previous_task = TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_CONVERT_DATE_FORMAT, WhenSimpleTest(), previous_task
        )
        correct1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest(),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        output1 = ConvertDateFormatTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        config_dict = {
            K_FIELDS: ["field1", "field2", "field3"],
            K_ACCEPTED_FORMATS: ["format1", "format2", "format3"],
            K_TARGET_FORMAT: "targetFormat",
            K_ALLOW_BLANK: False
        }
        previous_task = TestFieldCreatorTask("prevTask", ["field1", "field2"])
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_CONVERT_DATE_FORMAT, WhenSimpleTest(), previous_task
        )
        try:
            ConvertDateFormatTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" was expected by %s task "%s", but was not found in resulting fields ' \
                       'from %s task "%s". (File "%s")' % (
                           "field3", K_CONVERT_DATE_FORMAT, "taskName", previous_task.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_with_timezone(self):
        config_dict = {
            K_FIELDS: ["field1", "field2", "field3"],
            K_ACCEPTED_FORMATS: ["format1", "format2", "format3"],
            K_TARGET_FORMAT: "targetFormat",
            K_ALLOW_BLANK: False,
            K_TIMEZONE: "America/New_York"
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_CONVERT_DATE_FORMAT, WhenSimpleTest(), None
        )
        correct1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest(),
            None,
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "America/New_York"
        )
        output1 = ConvertDateFormatTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_timezone(self):
        config_dict = {
            K_FIELDS: ["field1", "field2", "field3"],
            K_ACCEPTED_FORMATS: ["format1", "format2", "format3"],
            K_TARGET_FORMAT: "targetFormat",
            K_ALLOW_BLANK: False,
            K_TIMEZONE: "America/Zoo_York"
        }
        input1 = TaskParsingContext(
            YamlPathContext(CommandLineContext("", "", True, ""), "currentFile", "current.key", config_dict),
            "taskName", K_CONVERT_DATE_FORMAT, WhenSimpleTest(), None
        )
        try:
            ConvertDateFormatTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = f'Invalid timezone provided for {K_CONVERT_DATE_FORMAT} task ' \
                       f'"taskName": "America/Zoo_York". ' \
                       f'(File "currentFile")'
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = ConvertDateFormatTask(
            "taskName1",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        obj2 = ConvertDateFormatTask(
            "taskName2",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string1"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string2"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field4"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field4"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_accepted_format(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format4"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_target_format(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat1",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat2",
            False,
            "Asia/Singapore"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_allow_blank(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            True,
            "Asia/Singapore"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_timezone(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "Asia/Singapore"
        )
        obj2 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest("string"),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            "America/New_York"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_success(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            None,
            ["field1", "field2", "field3"],
            ["field1", "field2"],
            ["%d%m%Y", "%d-%b-%Y"],
            "%Y-%m-%dT%H:%M:%S%z",
            False,
            "Asia/Singapore"
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
            ), 1, {"field1": "09081965", "field2": "8-sep-2020", "field3": "10101965"}
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
            ), 1, {
                "field1": "1965-08-09T00:00:00+0730",
                "field2": "2020-09-08T00:00:00+0800",
                "field3": "10101965"
            }
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_blank(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            None,
            ["field1", "field2", "field3"],
            ["field1", "field2"],
            ["%d%m%Y", "%d-%b-%Y"],
            "%Y-%m-%d",
            True,
            commonconstants.DEFAULT_TIMEZONE
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
            ), 1, {"field1": "09081965", "field2": "", "field3": "10101965"}
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
            ), 1, {"field1": "1965-08-09", "field2": "", "field3": "10101965"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            None,
            ["field1", "field2", "field3"],
            ["field1", "field2"],
            ["%d%m%Y", "%d-%b-%Y"],
            "%Y-%m-%d",
            True,
            commonconstants.DEFAULT_TIMEZONE
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
            ), 1, {"field1": "09081965", "field3": "10101965"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field2"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_invalid(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            None,
            ["field1", "field2", "field3"],
            ["field1", "field2"],
            ["%d%m%Y", "%d-%b-%Y"],
            "%Y-%m-%d",
            False,
            commonconstants.DEFAULT_TIMEZONE
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
            ), 1, {"field1": "09081965", "field2": "thisisnotadate", "field3": "10101965"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not interpret date value "%s" in field "%s".' % ("thisisnotadate", "field2")
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest(),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field4"],
            ["%d%m%Y", "%d-%b-%Y"],
            "%Y-%m-%d",
            False,
            commonconstants.DEFAULT_TIMEZONE
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
            ), 1, {"field1": "09081965", "field2": "thisisnotadate", "field3": "10101965"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = ConvertDateFormatTask(
            "taskName",
            WhenSimpleTest(),
            ["field1", "field2", "field3"],
            ["field1", "field2", "field3"],
            ["format1", "format2", "format3"],
            "targetFormat",
            False,
            commonconstants.DEFAULT_TIMEZONE
        )
        correct1 = ["field1", "field2", "field3"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
