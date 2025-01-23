import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.config.classes import YamlPathContext, TaskParsingContext, Fileset, InputFile, Sheet
from dataunifier.parse.classes import ParseRowContext, ParseIteratorContext, ParseInputFileContext, ParseFilesetContext, \
    TestBogusDictWriter
from dataunifier.tasks.MapFieldsTask import Field, K_TARGET_FIELD, K_SRC_FIELDS, K_MANDATORY, MapFieldsTask, \
    K_MAP_FIELDS, K_FIELDS, K_IGNORE_CASE
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when import WhenFieldMatchesRegex
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestField(unittest.TestCase):
    def test_eq(self):
        obj1 = Field("targetField", ["srcField1", "srcField2"], True, False)
        obj2 = Field("targetField", ["srcField1", "srcField2"], True, False)
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_target_field(self):
        obj1 = Field("targetField1", ["srcField1", "srcField2"], True, False)
        obj2 = Field("targetField2", ["srcField1", "srcField2"], True, False)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_src_fields(self):
        obj1 = Field("targetField", ["srcField1", "srcField2"], True, False)
        obj2 = Field("targetField", ["srcField1", "srcField3"], True, False)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_mandatory(self):
        obj1 = Field("targetField", ["srcField1", "srcField2"], True, False)
        obj2 = Field("targetField", ["srcField1", "srcField2"], False, False)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_ignore_case(self):
        obj1 = Field("targetField", ["srcField1", "srcField2"], True, True)
        obj2 = Field("targetField", ["srcField1", "srcField2"], False, False)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestMapFieldsTask(unittest.TestCase):
    def test_create_from_config_success(self):
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", True, "configFilePath"),
                "currentFile",
                "current.key",
                {
                    K_FIELDS: [
                        {
                            K_TARGET_FIELD: "targetField1"
                        },
                        {
                            K_TARGET_FIELD: "targetField2",
                            K_SRC_FIELDS: ["srcField2a", "srcField2b"]
                        },
                        {
                            K_TARGET_FIELD: "targetField3",
                            K_SRC_FIELDS: ["srcField3a", "srcField3b"],
                            K_MANDATORY: False
                        }
                    ]
                }
            ),
            "taskName",
            K_MAP_FIELDS,
            None,
            TestFieldCreatorTask("prevTask", ["srcField2a"])
        )
        correct1 = MapFieldsTask("taskName", [
            Field("targetField1", [], False, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False),
            Field("targetField3", ["srcField3a", "srcField3b"], False, False)
        ])
        output1 = MapFieldsTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_success_with_ignore_case(self):
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", True, "configFilePath"),
                "currentFile",
                "current.key",
                {
                    K_IGNORE_CASE: True,
                    K_FIELDS: [
                        {
                            K_TARGET_FIELD: "targetField1"
                        },
                        {
                            K_TARGET_FIELD: "targetField2",
                            K_SRC_FIELDS: ["srcField2a", "srcField2b"],
                            K_IGNORE_CASE: False
                        },
                        {
                            K_TARGET_FIELD: "targetField3",
                            K_SRC_FIELDS: ["srcField3a", "srcField3b"],
                            K_MANDATORY: False
                        }
                    ]
                }
            ),
            "taskName",
            K_MAP_FIELDS,
            None,
            TestFieldCreatorTask("prevTask", ["srcField2a"])
        )
        correct1 = MapFieldsTask("taskName", [
            Field("targetField1", [], False, True),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False),
            Field("targetField3", ["srcfield3a", "srcfield3b"], False, True)
        ])
        output1 = MapFieldsTask.create_from_config(input1)
        self.assertEqual(correct1, output1)

    def test_create_from_config_missing_field(self):
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", True, "configFilePath"),
                "currentFile",
                "current.key",
                {
                    K_FIELDS: [
                        {
                            K_TARGET_FIELD: "targetField1"
                        },
                        {
                            K_TARGET_FIELD: "targetField2",
                            K_SRC_FIELDS: ["srcField2a", "srcField2b"]
                        },
                        {
                            K_TARGET_FIELD: "targetField3",
                            K_SRC_FIELDS: ["srcField3a", "srcField3b"],
                            K_MANDATORY: False
                        }
                    ]
                }
            ),
            "taskName",
            K_MAP_FIELDS,
            None,
            TestFieldCreatorTask("prevTask", ["srcField3a"])
        )
        try:
            MapFieldsTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Fields "%s" are expected by %s task "%s" but was not found in resulting fields of %s ' \
                       'task "%s". (File "%s")' % (
                           'srcField2a" or "srcField2b', K_MAP_FIELDS, "taskName",
                           TestFieldCreatorTask.get_task_type_string(),
                           "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_clashing_field(self):
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", True, "configFilePath"),
                "currentFile",
                "current.key",
                {
                    K_FIELDS: [
                        {
                            K_TARGET_FIELD: "targetField1"
                        },
                        {
                            K_TARGET_FIELD: "targetField2",
                            K_SRC_FIELDS: ["srcField2a", "srcField2b"]
                        },
                        {
                            K_TARGET_FIELD: "targetField3",
                            K_SRC_FIELDS: ["srcField3a", "srcField3b"],
                            K_MANDATORY: False
                        }
                    ]
                }
            ),
            "taskName",
            K_MAP_FIELDS,
            None,
            TestFieldCreatorTask("prevTask", ["srcField2a", "srcField2b"])
        )
        try:
            MapFieldsTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = '%s "%s" and "%s" in %s task "%s" map to the same %s and were both found in ' \
                       'resulting fields of %s task "%s". (File "%s")' % (
                           K_SRC_FIELDS, "srcField2a", "srcField2b", K_MAP_FIELDS, "taskName", K_TARGET_FIELD,
                           TestFieldCreatorTask.get_task_type_string(), "prevTask", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_create_from_config_with_when(self):
        input1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", True, "configFilePath"),
                "currentFile",
                "current.key",
                {
                    K_FIELDS: [
                        {
                            K_TARGET_FIELD: "targetField1"
                        },
                        {
                            K_TARGET_FIELD: "targetField2",
                            K_SRC_FIELDS: ["srcField2a", "srcField2b"]
                        },
                        {
                            K_TARGET_FIELD: "targetField3",
                            K_SRC_FIELDS: ["srcField3a", "srcField3b"],
                            K_MANDATORY: False
                        }
                    ]
                }
            ),
            "taskName",
            K_MAP_FIELDS,
            WhenSimpleTest("when"),
            TestFieldCreatorTask("prevTask", ["srcField2a"])
        )
        try:
            MapFieldsTask.create_from_config(input1)
            self.fail()
        except ConfigException as e:
            correct1 = '"when" cannot be used with a %s task. (File "%s", task "%s")' % (
                K_MAP_FIELDS, "currentFile", "taskName"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_task_type_string(self):
        correct1 = K_MAP_FIELDS
        output1 = MapFieldsTask.get_task_type_string()
        self.assertEqual(correct1, output1)

    def test_transform_success(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
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
            ), 1, {"srcField1a": "value1", "srcField2b": "value2"}
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
            ), 1, {"targetField1": "value1", "targetField2": "value2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_success_with_ignore_case(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcfield1a", "srcfield1b"], True, True),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
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
            ), 1, {"sRcFiElD1A": "value1", "srcField2b": "value2"}
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
            ), 1, {"targetField1": "value1", "targetField2": "value2"}
        )
        output1 = obj1.transform(input1)
        self.assertEqual(correct1, output1)

    def test_transform_clashing_field(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
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
            ), 1, {"srcField1a": "value1", "srcField1b": "value2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Fields "%s" and "%s" both exist and are mapped to the same target field "%s"' % (
                "srcField1a", "srcField1b", "targetField1"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_transform_missing_field(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
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
            ), 1, {"srcField2a": "value1", "srcField3b": "value2"}
        )
        try:
            obj1.transform(input1)
            self.fail()
        except TransformationException as e:
            correct1 = 'Could not find any fields to map to target field "%s". Expected source fields: "%s"' % (
                "targetField1", 'srcField1a", "srcField1b'
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_get_resulting_fields(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
        correct1 = ["targetField1", "targetField2"]
        output1 = obj1.get_resulting_fields()
        self.assertEqual(correct1, output1)

    def test_is_conditional(self):
        correct1 = False
        output1 = MapFieldsTask.is_conditional()
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
        obj2 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = MapFieldsTask("name1", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
        obj2 = MapFieldsTask("name2", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2b"], True, False)
        ])
        obj2 = MapFieldsTask("name", [
            Field("targetField1", ["srcField1a", "srcField1b"], True, False),
            Field("targetField2", ["srcField2a", "srcField2c"], True, False)
        ])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)
