import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.config.classes import Fileset, InputFile, Sheet
from dataunifier.parse.classes import TestBogusDictWriter, ParseFilesetContext, ParseInputFileContext, \
    ParseRowContext, ParseIteratorContext
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask


class TestTestBogusDictWriter(unittest.TestCase):
    def test_eq(self):
        obj1 = TestBogusDictWriter("string1")
        obj2 = TestBogusDictWriter("string1")
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne(self):
        obj1 = TestBogusDictWriter("string1")
        obj2 = TestBogusDictWriter("string2")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_writerow(self):
        obj1 = TestBogusDictWriter("")
        input1 = {"field1a": "value1a", "field1b": "value1b"}
        correct1 = [input1]
        obj1.writerow(input1)
        output1 = obj1.rowdicts
        self.assertEqual(correct1, output1)
        input2 = {"field2a": "value2a", "field2b": "value2b"}
        correct2 = [input1, input2]
        obj1.writerow(input2)
        output2 = obj1.rowdicts
        self.assertEqual(correct2, output2)

    def test_writerows(self):
        obj1 = TestBogusDictWriter("")
        input1 = [
            {"field1a": "value1a", "field1b": "value1b"},
            {"field2a": "value2a", "field2b": "value2b"}
        ]
        correct1 = [
            {"field1a": "value1a", "field1b": "value1b"},
            {"field2a": "value2a", "field2b": "value2b"}
        ]
        obj1.writerows(input1)
        output1 = obj1.rowdicts
        self.assertEqual(correct1, output1)
        input2 = [
            {"field3a": "value3a", "field3b": "value3b"},
            {"field4a": "value4a", "field4b": "value4b"}
        ]
        correct2 = [
            {"field1a": "value1a", "field1b": "value1b"},
            {"field2a": "value2a", "field2b": "value2b"},
            {"field3a": "value3a", "field3b": "value3b"},
            {"field4a": "value4a", "field4b": "value4b"}
        ]
        obj1.writerows(input2)
        output2 = obj1.rowdicts
        self.assertEqual(correct2, output2)


class TestParseFilesetContext(unittest.TestCase):
    def test_eq(self):
        obj1 = ParseFilesetContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        obj2 = ParseFilesetContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_command_line_ctxt(self):
        obj1 = ParseFilesetContext(
            CommandLineContext("inputDir1", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        obj2 = ParseFilesetContext(
            CommandLineContext("inputDir2", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_writer(self):
        obj1 = ParseFilesetContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        obj2 = ParseFilesetContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer2"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fileset(self):
        obj1 = ParseFilesetContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset1",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        obj2 = ParseFilesetContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            TestBogusDictWriter("writer1"),
            Fileset(
                "fileset2",
                ["field1"],
                [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                TestFieldCreatorTask("task1", ["field1"])
            )
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestParseInputFileContext(unittest.TestCase):
    def test_eq(self):
        obj1 = ParseInputFileContext(
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
        )
        obj2 = ParseInputFileContext(
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
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = ParseInputFileContext(
            ParseFilesetContext(
                CommandLineContext("inputDir1", "outputFilePath", False, "configFilePath"),
                TestBogusDictWriter("writer1"),
                Fileset(
                    "fileset1",
                    ["field1"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    TestFieldCreatorTask("task1", ["field1"])
                )
            ),
            InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
        )
        obj2 = ParseInputFileContext(
            ParseFilesetContext(
                CommandLineContext("inputDir2", "outputFilePath", False, "configFilePath"),
                TestBogusDictWriter("writer1"),
                Fileset(
                    "fileset1",
                    ["field1"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    TestFieldCreatorTask("task1", ["field1"])
                )
            ),
            InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_input_file(self):
        obj1 = ParseInputFileContext(
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
        )
        obj2 = ParseInputFileContext(
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
            InputFile("inputFile2", ["regex1"], [Sheet(["regex1"], True)])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestParseIteratorContext(unittest.TestCase):
    def test_eq(self):
        obj1 = ParseIteratorContext(
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
        )
        obj2 = ParseIteratorContext(
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
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = ParseIteratorContext(
            ParseInputFileContext(
                ParseFilesetContext(
                    CommandLineContext("inputDir1", "outputFilePath", False, "configFilePath"),
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
        )
        obj2 = ParseIteratorContext(
            ParseInputFileContext(
                ParseFilesetContext(
                    CommandLineContext("inputDir2", "outputFilePath", False, "configFilePath"),
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
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_filepath(self):
        obj1 = ParseIteratorContext(
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
            "filepath1", "sheet", ["row1", "row2"]
        )
        obj2 = ParseIteratorContext(
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
            "filepath2", "sheet", ["row1", "row2"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_sheet(self):
        obj1 = ParseIteratorContext(
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
            "filepath", "sheet1", ["row1", "row2"]
        )
        obj2 = ParseIteratorContext(
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
            "filepath", "sheet2", ["row1", "row2"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_iterator(self):
        obj1 = ParseIteratorContext(
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
        )
        obj2 = ParseIteratorContext(
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
            "filepath", "sheet", ["row1", "row3"]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestParseRowContext(unittest.TestCase):
    def test_with_updated_rowdict(self):
        obj1 = ParseRowContext(
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
            ), 1, {"key1": "value1"}
        )
        input1 = {"key2": "value2"}
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
            ), 1, input1
        )
        output1 = obj1.with_updated_rowdict(input1)
        self.assertEqual(correct1, output1)

    def test_eq(self):
        obj1 = ParseRowContext(
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
            ), 1, {"key": "value"}
        )
        obj2 = ParseRowContext(
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
            ), 1, {"key": "value"}
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir1", "outputFilePath", False, "configFilePath"),
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
            ), 1, {"key": "value"}
        )
        obj2 = ParseRowContext(
            ParseIteratorContext(
                ParseInputFileContext(
                    ParseFilesetContext(
                        CommandLineContext("inputDir2", "outputFilePath", False, "configFilePath"),
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
            ), 1, {"key": "value"}
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_row_number(self):
        obj1 = ParseRowContext(
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
            ), 1, {"key": "value"}
        )
        obj2 = ParseRowContext(
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
            ), 2, {"key": "value"}
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_rowdict(self):
        obj1 = ParseRowContext(
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
            ), 1, {"key": "value1"}
        )
        obj2 = ParseRowContext(
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
            ), 1, {"key": "value2"}
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)
