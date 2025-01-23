import re
import unittest

import dataunifier.common.constants as commonconstants

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.config import config
from dataunifier.config.classes import Fileset, ConfigContext, InputFile, Sheet
from dataunifier.common.exceptions import ConfigException
from dataunifier.tasks import MapFieldsTask, SetFieldValueTask, ConvertDateFormatTask, LowercaseTask, UppercaseTask, \
    RegexReplaceTask, DiscardRecordTask, DiscardFieldsTask, CopyFieldValueTask, ConcatenateFieldsTask, \
    CsvLookupReplaceTask, CsvMatchTask, ArithmeticTask, FuzzyMatchReplaceTask, ReplaceTask
from dataunifier.tasks.BlockTask import BlockTask
from dataunifier.tasks.FuzzyMatchReplaceTask import JaccardRule
from dataunifier.tasks.MapFieldsTask import Field
from dataunifier.tasks.RegexReplaceTask import RegexReplaceRule
from dataunifier.tasks.ReplaceTask import ReplaceRule
from dataunifier.when import WhenFieldMatchesRegex, And, Or, Not
from tests.constants import TESTCONFIG_PATH, TESTFILESET_PATH, TESTCONFIG_ILLEGALBLOCK_PATH


class TestGetFields(unittest.TestCase):
    def test_same(self):
        fs1 = Fileset("fileset1", ["field1", "field2", "field3"], None, [])
        fs2 = Fileset("fileset1", ["field1", "field2", "field3"], None, [])
        fs3 = Fileset("fileset1", ["field1", "field2", "field3"], None, [])
        input1 = [fs1, fs2, fs3]
        correct1 = ["field1", "field2", "field3"]
        output1 = config.get_fields(input1)
        self.assertEqual(correct1, output1)

    def test_diff(self):
        fs1 = Fileset("fileset1", ["field1", "field2", "field3"], None, [])
        fs2 = Fileset("fileset2", ["field1", "field2", "field3"], None, [])
        fs3 = Fileset("fileset3", ["field1", "field2", "field4"], None, [])
        input1 = [fs1, fs2, fs3]
        try:
            config.get_fields(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Resulting fields for filesets do not match.\n' \
                       'Fields for fileset "fileset1": ["field1", "field2", "field3"]\n' \
                       'Fields for fileset "fileset2": ["field1", "field2", "field3"]\n' \
                       'Fields for fileset "fileset3": ["field1", "field2", "field4"]'
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestGetContext(unittest.TestCase):
    def test_success(self):
        input1 = CommandLineContext("", "", True, TESTCONFIG_PATH)
        correct1 = ConfigContext(
            input1,
            ["targetField0", "targetField1"],
            [
                Fileset(
                    "Test Fileset",
                    ["targetField0", "targetField1"],
                    [
                        InputFile("Test CSV Simple", ["^testcsv.csv$"], None),
                        InputFile("Test CSV Multiple Regex", ["^testcsv1.csv$", "^testcsv1.csv$"], None),
                        InputFile("Test Excel 1", ["^testexcel1.xlsx$"], [Sheet(["^sheet1$"], True)]),
                        InputFile("Test Excel 2", ["^testexcel2.xlsx$"], [Sheet(["^sheet\\d$"], False)])
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("targetField0", [], False, True),
                            Field("targetField1", ["srcfield1"], True, True),
                            Field("targetField2", ["srcField2a", "srcField2b"], True, False),
                            Field("targetField3", ["srcfield3a", "srcfield3b"], False, True)
                        ]),
                        BlockTask(
                            "Task Block",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            [
                                SetFieldValueTask(
                                    "Set targetField0 to 'chippermonkey'",
                                    WhenFieldMatchesRegex("someField", ["someRegex"]),
                                    ["targetField0", "targetField1", "targetField2", "targetField3"],
                                    "targetField0",
                                    "chippermonkey"
                                ),
                                ConvertDateFormatTask(
                                    "Interpret Date",
                                    WhenFieldMatchesRegex("someField", ["someRegex"]),
                                    ["targetField0", "targetField1", "targetField2", "targetField3"],
                                    ["targetField1", "targetField2"],
                                    ["format1", "format2"],
                                    "targetFormat",
                                    False,
                                    commonconstants.DEFAULT_TIMEZONE
                                )
                            ]
                        ),
                        LowercaseTask(
                            "Lowercase",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField0", "targetField3"]
                        ),
                        UppercaseTask(
                            "Uppercase",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField1", "targetField2"]
                        ),
                        ReplaceTask(
                            "Replace",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField1"],
                            ReplaceTask.E_FAIL,
                            False,
                            [
                                ReplaceRule(["This"], "That"),
                                ReplaceRule(["anything", "something"], "nothing")
                            ],
                            TESTFILESET_PATH
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField1"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("^This$")], "That"),
                                RegexReplaceRule([re.compile("^anything$"), re.compile("something")], "nothing")
                            ],
                            TESTFILESET_PATH
                        ),
                        DiscardRecordTask(
                            "Discard Record",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"]
                        ),
                        CopyFieldValueTask(
                            "Copy fields",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            "targetField0", ["targetField2", "targetField3"]
                        ),
                        ConcatenateFieldsTask(
                            "Concatenate fields",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField0", "targetField1"], "targetField2", "_"
                        ),
                        CsvLookupReplaceTask(
                            "CSV Lookup",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField0", "targetField1"],
                            {"lookup1": "value1", "lookup2": "value2"},
                            CsvLookupReplaceTask.E_BLANK
                        ),
                        CsvMatchTask(
                            "CSV Match",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField2"],
                            {"lookup1", "lookup2"},
                            "match",
                            "unmatch"
                        ),
                        ArithmeticTask(
                            "Arithmetic",
                            WhenFieldMatchesRegex("someField", ["someRegex"]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            "targetField0",
                            "targetField1",
                            "targetField2",
                            ArithmeticTask.E_MULTIPLY,
                            True
                        ),
                        FuzzyMatchReplaceTask(
                            "Fuzzy Match",
                            And([
                                Not(WhenFieldMatchesRegex("someField1", ["someRegex1"])),
                                Or([
                                    WhenFieldMatchesRegex("someField2", ["someRegex2"]),
                                    WhenFieldMatchesRegex("someField3", ["someRegex3"]),
                                ])
                            ]),
                            ["targetField0", "targetField1", "targetField2", "targetField3"],
                            ["targetField0"],
                            FuzzyMatchReplaceTask.E_JACCARD,
                            [
                                JaccardRule("string1", "replacement1", FuzzyMatchReplaceTask.DEFAULT_NGRAM_SIZE),
                                JaccardRule("string2a", "replacement2", FuzzyMatchReplaceTask.DEFAULT_NGRAM_SIZE),
                                JaccardRule("string2b", "replacement2", FuzzyMatchReplaceTask.DEFAULT_NGRAM_SIZE)
                            ],
                            0.5,
                            FuzzyMatchReplaceTask.E_FAIL
                        ),
                        DiscardFieldsTask("Discard Fields",
                                          ["targetField0", "targetField1", "targetField2", "targetField3"],
                                          ["targetField2", "targetField3"])
                    ]
                )
            ]
        )
        output1 = config.get_context(input1)
        self.assertEqual(correct1, output1)

    def test_illegal_block(self):
        input1 = CommandLineContext("", "", True, TESTCONFIG_ILLEGALBLOCK_PATH)
        try:
            config.get_context(input1)
            self.fail()
        except ConfigException as e:
            correct1 = f'{MapFieldsTask.get_task_type_string()} tasks cannot be put inside a task block, ' \
                       f'because they cannot be used with "when".' \
                       f'(File "{TESTCONFIG_ILLEGALBLOCK_PATH}", Task "Map Fields")'
            output1 = e.message
            self.assertEqual(correct1, output1)
