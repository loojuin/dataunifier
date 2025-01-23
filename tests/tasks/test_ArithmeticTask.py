import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import TransformationException, ConfigException
from dataunifier.config.classes import Fileset, InputFile, Sheet, TaskParsingContext, YamlPathContext
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks import ArithmeticTask
from dataunifier.tasks.ArithmeticTask import K_ARITHMETIC, E_ADD, E_SUBTRACT, E_MULTIPLY, E_DIVIDE, K_LEFT_FIELD, \
    K_RIGHT_FIELD, K_RESULT_FIELD, K_OPERATION, K_BLANK_IS_ZERO
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestArithmeticTask(unittest.TestCase):
    def test_create_from_config_success(self):
        config_dict = {
            K_LEFT_FIELD: "field1",
            K_RIGHT_FIELD: "field2",
            K_RESULT_FIELD: "field3",
            K_OPERATION: E_ADD,
            K_BLANK_IS_ZERO: True
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_ARITHMETIC,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        correct1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, True
        )
        output1 = ArithmeticTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_blank_is_zero(self):
        config_dict = {
            K_LEFT_FIELD: "field1",
            K_RIGHT_FIELD: "field2",
            K_RESULT_FIELD: "field3",
            K_OPERATION: E_ADD
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_ARITHMETIC,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        correct1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        output1 = ArithmeticTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_invalid_operation(self):
        config_dict = {
            K_LEFT_FIELD: "field1",
            K_RIGHT_FIELD: "field2",
            K_RESULT_FIELD: "field3",
            K_OPERATION: "invalid",
            K_BLANK_IS_ZERO: True
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_ARITHMETIC,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field3"])
        )
        try:
            ArithmeticTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Invalid value for key "%s": "%s". Accepted values are: "%s". (File "%s")' % (
                "current.key.%s" % K_OPERATION, "invalid",
                '", "'.join([E_ADD, E_SUBTRACT, E_MULTIPLY, E_DIVIDE]), "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_left_field(self):
        config_dict = {
            K_LEFT_FIELD: "field1",
            K_RIGHT_FIELD: "field2",
            K_RESULT_FIELD: "field3",
            K_OPERATION: E_ADD,
            K_BLANK_IS_ZERO: True
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_ARITHMETIC,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field4", "field2", "field3"])
        )
        try:
            ArithmeticTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       'preceding %s task "%s". (File "%s")' % (
                           "field1", K_ARITHMETIC, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_right_field(self):
        config_dict = {
            K_LEFT_FIELD: "field1",
            K_RIGHT_FIELD: "field2",
            K_RESULT_FIELD: "field3",
            K_OPERATION: E_ADD,
            K_BLANK_IS_ZERO: True
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_ARITHMETIC,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field4", "field3"])
        )
        try:
            ArithmeticTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       'preceding %s task "%s". (File "%s")' % (
                           "field2", K_ARITHMETIC, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_missing_result_field(self):
        config_dict = {
            K_LEFT_FIELD: "field1",
            K_RIGHT_FIELD: "field2",
            K_RESULT_FIELD: "field3",
            K_OPERATION: E_ADD,
            K_BLANK_IS_ZERO: True
        }
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", config_dict
            ),
            "taskName",
            K_ARITHMETIC,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["field1", "field2", "field4"])
        )
        try:
            ArithmeticTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                       'preceding %s task "%s". (File "%s")' % (
                           "field3", K_ARITHMETIC, "taskName", TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_ARITHMETIC
        output1 = ArithmeticTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = True
        output1 = ArithmeticTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = ArithmeticTask(
            "taskName1", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName2", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when1"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when2"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_resulting_fields(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field4"], "field1", "field2", "field3",
            E_ADD, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_left_field(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field2", "field2", "field3",
            E_ADD, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_right_field(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field3", "field3",
            E_ADD, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_result_field(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field4",
            E_ADD, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_operation(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_SUBTRACT, False
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_blank_is_zero(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        obj2 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, True
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_transform_when_none(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "103", "field2": "20", "field3": "replaceMe"}
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
            ), 1, {"field1": "103", "field2": "20", "field3": "123"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_true(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("true"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "103", "field2": "20", "field3": "replaceMe"}
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
            ), 1, {"field1": "103", "field2": "20", "field3": "123"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_when_false(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest(), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "103", "field2": "20", "field3": "replaceMe"}
        )
        correct1 = input1
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_subtract_int(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_SUBTRACT, False
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
            ), 1, {"field1": "123", "field2": "20", "field3": "replaceMe"}
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
            ), 1, {"field1": "123", "field2": "20", "field3": "103"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_multiply_int(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_MULTIPLY, False
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
            ), 1, {"field1": "114", "field2": "10043", "field3": "replaceMe"}
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
            ), 1, {"field1": "114", "field2": "10043", "field3": "1144902"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_divide_int(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_DIVIDE, False
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
            ), 1, {"field1": "1004", "field2": "72", "field3": "replaceMe"}
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
            ), 1, {"field1": "1004", "field2": "72", "field3": "13.944444444444445"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_add_float(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "replaceMe"}
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "6.406073200000001"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_subtract_float(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_SUBTRACT, False
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "replaceMe"}
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "-3.8401068"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_multiply_float(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_MULTIPLY, False
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "replaceMe"}
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "6.572838402088001"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_divide_float(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_DIVIDE, False
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "replaceMe"}
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
            ), 1, {"field1": "1.2829832", "field2": "5.12309", "field3": "0.2504315169165484"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_divide_by_zero(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_DIVIDE, False
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
            ), 1, {"field1": "1", "field2": "0", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Cannot divide by zero (value of field "%s" is zero).' % "field2"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_left_field_blank(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_MULTIPLY, True
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
            ), 1, {"field1": "", "field2": "12321", "field3": "replaceMe"}
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
            ), 1, {"field1": "", "field2": "12321", "field3": "0"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_right_field_blank(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_MULTIPLY, True
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
            ), 1, {"field1": "12321", "field2": "", "field3": "replaceMe"}
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
            ), 1, {"field1": "12321", "field2": "", "field3": "0"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_left_field_invalid(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "notANumber", "field2": "12321", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Value of field "%s" is not a number: "%s"' % ("field1", "notANumber")
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_right_field_invalid(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "12321", "field2": "notANumber", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Value of field "%s" is not a number: "%s"' % ("field2", "notANumber")
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_missing_left_field(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field4", "field2", "field3",
            E_ADD, False
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
            ), 1, {"field1": "12321", "field2": "notANumber", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field4"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_missing_right_field(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field4", "field3",
            E_ADD, False
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
            ), 1, {"field1": "12321", "field2": "notANumber", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field4"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_missing_result_field(self):
        obj1 = ArithmeticTask(
            "taskName", None, ["field1", "field2", "field3"], "field1", "field2", "field4",
            E_ADD, False
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
            ), 1, {"field1": "12321", "field2": "notANumber", "field3": "replaceMe"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find field "%s".' % "field4"
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = ArithmeticTask(
            "taskName", WhenSimpleTest("when"), ["field1", "field2", "field3"], "field1", "field2", "field3",
            E_ADD, False
        )
        correct1 = ["field1", "field2", "field3"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)
