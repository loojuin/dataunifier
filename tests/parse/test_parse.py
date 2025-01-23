import os
import re
import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.common.exceptions import InputFileException, ParsingException
from dataunifier.config.classes import ConfigContext, Fileset, InputFile, Sheet
from dataunifier.parse import parse
from dataunifier.parse.classes import TestBogusDictWriter
from dataunifier.tasks import MapFieldsTask, CopyFieldValueTask, RegexReplaceTask
from dataunifier.tasks.MapFieldsTask import Field
from dataunifier.tasks.RegexReplaceTask import RegexReplaceRule
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from tests.constants import TESTASSETS_DIR, TESTCSV_NAME, TESTXLS_NAME, TESTTXT_NAME, TESTXLSENCRYPT_NAME, \
    TESTXLSENCRYPT_PATH


class TestParse(unittest.TestCase):
    def test_start_csv(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input CSV", ["^%s$" % TESTCSV_NAME], None)
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("field1", ["lookup"], True, False),
                            Field("field2", ["value"], True, False),
                            Field("field3", [], False, False)
                        ]),
                        CopyFieldValueTask(
                            "Copy Field Value",
                            None,
                            ["field1", "field2", "field3"],
                            "field2",
                            ["field3"]
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            None,
                            ["field1", "field2", "field3"],
                            ["field2"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("value")], "volley")
                            ],
                            "rulesFile"
                        )
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        correct1 = [
            {"field1": "lookup1", "field2": "volley1", "field3": "value1"},
            {"field1": "lookup2", "field2": "volley2", "field3": "value2"}
        ]
        parse.start(input1, writer)
        output1 = writer.rowdicts
        self.assertEqual(correct1, output1)

    def test_start_csv_second_file_regex_match(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input CSV", ["^nonexistent.csv$", "^%s$" % TESTCSV_NAME], None)
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("field1", ["lookup"], True, False),
                            Field("field2", ["value"], True, False),
                            Field("field3", [], False, False)
                        ]),
                        CopyFieldValueTask(
                            "Copy Field Value",
                            None,
                            ["field1", "field2", "field3"],
                            "field2",
                            ["field3"]
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            None,
                            ["field1", "field2", "field3"],
                            ["field2"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("value")], "volley")
                            ],
                            "rulesFile"
                        )
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        correct1 = [
            {"field1": "lookup1", "field2": "volley1", "field3": "value1"},
            {"field1": "lookup2", "field2": "volley2", "field3": "value2"}
        ]
        parse.start(input1, writer)
        output1 = writer.rowdicts
        self.assertEqual(correct1, output1)

    def test_start_xls(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input Excel", ["^%s$" % TESTXLS_NAME], [
                            Sheet(["^readme$"], True),
                            Sheet(["^canre.+$"], True)
                        ])
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("field1", ["lookup", "MyLookup"], True, False),
                            Field("field2", ["value", "MyValue"], True, False),
                            Field("field3", [], False, False),
                            Field("field4", ["blank_field"], True, False),
                            Field("field5", ["int_field", "MyInt"], True, False),
                            Field("field6", ["float_field", "MyFloat"], True, False)
                        ]),
                        CopyFieldValueTask(
                            "Copy Field Value",
                            None,
                            ["field1", "field2", "field3"],
                            "field2",
                            ["field3"]
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            None,
                            ["field1", "field2", "field3"],
                            ["field2"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("value")], "volley")
                            ],
                            "rulesFile"
                        )
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        correct1 = [
            {
                "field1": "lookup1", "field2": "volley1", "field3": "value1",
                "field4": "", "field5": "", "field6": "1.11"
            },
            {
                "field1": "lookup2", "field2": "volley2", "field3": "value2",
                "field4": "", "field5": "2", "field6": "2.22"
            },
            {
                "field1": "lookup5", "field2": "volley5", "field3": "value5",
                "field4": "", "field5": "5", "field6": "5.55"
            },
            {
                "field1": "lookup6", "field2": "volley6", "field3": "value6",
                "field4": "", "field5": "6", "field6": "6.66"
            },
        ]
        parse.start(input1, writer)
        output1 = writer.rowdicts
        self.assertEqual(correct1, output1)

    def test_start_xls_encrypted(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input Excel", ["^%s$" % TESTXLSENCRYPT_NAME], [
                            Sheet(["^readme$"], True),
                            Sheet(["^canre.+$"], True)
                        ])
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("field1", ["lookup", "MyLookup"], True, False),
                            Field("field2", ["value", "MyValue"], True, False),
                            Field("field3", [], False, False)
                        ]),
                        CopyFieldValueTask(
                            "Copy Field Value",
                            None,
                            ["field1", "field2", "field3"],
                            "field2",
                            ["field3"]
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            None,
                            ["field1", "field2", "field3"],
                            ["field2"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("value")], "volley")
                            ],
                            "rulesFile"
                        )
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        try:
            parse.start(input1, writer)
            self.fail()
        except InputFileException as e:
            correct1 = f'Could not read Excel file "{TESTXLSENCRYPT_PATH}". This could mean that it is ' \
                       f'encrypted with a password, or corrupted. Please remove the password (if any), ' \
                       f'and ensure it is not corrupted.'
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_parse_unsupported(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input Text File", ["^%s$" % TESTTXT_NAME], None)
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("field1", ["lookup", "MyLookup"], True, False),
                            Field("field2", ["value", "MyValue"], True, False),
                            Field("field3", [], False, False)
                        ]),
                        CopyFieldValueTask(
                            "Copy Field Value",
                            None,
                            ["field1", "field2", "field3"],
                            "field2",
                            ["field3"]
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            None,
                            ["field1", "field2", "field3"],
                            ["field2"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("value")], "volley")
                            ],
                            "rulesFile"
                        )
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        try:
            parse.start(input1, writer)
            self.fail()
        except InputFileException as e:
            correct1 = 'File "%s" has an unsupported format: "%s". Only CSVs and Excel files are accepted. ' \
                       '(Input File "%s")' % (
                           os.path.join(TESTASSETS_DIR, TESTTXT_NAME), "txt", "Input Text File"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_parse_missing_sheet(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input Excel", ["^%s$" % TESTXLS_NAME], [
                            Sheet(["^nonexistent$", "^noway$"], True)
                        ])
                    ],
                    [
                        MapFieldsTask("Map Fields", [
                            Field("field1", ["lookup", "MyLookup"], True, False),
                            Field("field2", ["value", "MyValue"], True, False),
                            Field("field3", [], False, False)
                        ]),
                        CopyFieldValueTask(
                            "Copy Field Value",
                            None,
                            ["field1", "field2", "field3"],
                            "field2",
                            ["field3"]
                        ),
                        RegexReplaceTask(
                            "Regex Replace",
                            None,
                            ["field1", "field2", "field3"],
                            ["field2"],
                            RegexReplaceTask.E_FAIL,
                            False,
                            [
                                RegexReplaceRule([re.compile("value")], "volley")
                            ],
                            "rulesFile"
                        )
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        try:
            parse.start(input1, writer)
            self.fail()
        except InputFileException as e:
            correct1 = 'Could not find any sheet name matching patterns "%s" in file "%s". (Input File "%s")' % (
                '", "'.join(["^nonexistent$", "^noway$"]), os.path.join(TESTASSETS_DIR, TESTXLS_NAME),
                "Input Excel"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_start_transformation_exception_without_sheet(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input CSV", ["^%s$" % TESTCSV_NAME], None)
                    ],
                    [
                        TestFieldCreatorTask("Fail", ["field1", "field2", "field3"])
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        try:
            parse.start(input1, writer)
            self.fail()
        except ParsingException as e:
            correct1 = 'When executing task "%s" on row %d of file "%s": %s' % (
                "Fail", 1, os.path.join(TESTASSETS_DIR, TESTCSV_NAME),
                TestFieldCreatorTask.TRANSFORMATION_EXCEPTION_MESSAGE
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_start_transformation_exception_with_sheet(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input Excel", ["^%s$" % TESTXLS_NAME], [
                            Sheet(["^readme$"], True),
                            Sheet(["^canre.+$"], True)
                        ])
                    ],
                    [
                        TestFieldCreatorTask("Fail", ["field1", "field2", "field3"])
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        try:
            parse.start(input1, writer)
            self.fail()
        except ParsingException as e:
            correct1 = 'When executing task "%s" on row %d of file "%s", sheet "%s": %s' % (
                "Fail", 1, os.path.join(TESTASSETS_DIR, TESTXLS_NAME), "readme",
                TestFieldCreatorTask.TRANSFORMATION_EXCEPTION_MESSAGE
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_start_missing_file(self):
        input1 = ConfigContext(
            CommandLineContext(TESTASSETS_DIR, "outputFilePath", False, "configFilePath"),
            ["field1", "field2", "field3"],
            [
                Fileset(
                    "Test",
                    ["field1", "field2", "field3"],
                    [
                        InputFile("Input CSV", ["^%s$" % "nonexistent.csv"], None)
                    ],
                    [
                        TestFieldCreatorTask("Fail", ["field1", "field2", "field3"])
                    ]
                )
            ]
        )
        writer = TestBogusDictWriter("")
        try:
            parse.start(input1, writer)
            self.fail()
        except InputFileException as e:
            correct1 = 'Could not find any file names matching patterns "%s" in input directory "%s". ' \
                       '(Input File "%s")' % (
                           "^nonexistent.csv$", TESTASSETS_DIR, "Input CSV"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)
