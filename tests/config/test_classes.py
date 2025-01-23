import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.config.classes import YamlPathContext, TaskParsingContext, ConfigContext, Fileset, InputFile, Sheet, \
    WhenParsingContext
from dataunifier.tasks.TestFieldCreatorTask import TestFieldCreatorTask
from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestYamlPathContext(unittest.TestCase):
    def test_eq(self):
        obj1 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key", "value"
        )
        obj2 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key", "value"
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = YamlPathContext(
            CommandLineContext("input_dir1", "output_dir", False, "config_file_path"),
            "currentFile", "current.key", "value"
        )
        obj2 = YamlPathContext(
            CommandLineContext("input_dir2", "output_dir", False, "config_file_path"),
            "currentFile", "current.key", "value"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_current_file(self):
        obj1 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile1", "current.key", "value"
        )
        obj2 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile2", "current.key", "value"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_current_key(self):
        obj1 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key1", "value"
        )
        obj2 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key2", "value"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_value(self):
        obj1 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key", "value1"
        )
        obj2 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key", "value2"
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_get_updated(self):
        obj1 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "current.key1", "value1"
        )
        next_key_path, next_value = "next.key2", "value2"
        correct1 = YamlPathContext(
            CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
            "currentFile", "next.key2", "value2"
        )
        output1 = obj1.get_updated(next_key_path, next_value)
        self.assertEqual(correct1, output1)


class TestWhenParsingContext(unittest.TestCase):
    def test_eq(self):
        obj1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path", 0
        )
        obj2 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path", 0
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir1", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path", 0
        )
        obj2 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir2", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path", 0
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_root_file(self):
        obj1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile1", "root.key.path", 0
        )
        obj2 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile2", "root.key.path", 0
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_root_key_path(self):
        obj1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path1", 0
        )
        obj2 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path2", 0
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_depth(self):
        obj1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path", 0
        )
        obj2 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value"
            ),
            "rootFile", "root.key.path", 1
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_next_depth(self):
        obj1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value1"
            ),
            "rootFile", "root.key.path", 0
        )
        input1 = YamlPathContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            "currentFile", "current.key", "value2"
        )
        correct1 = WhenParsingContext(
            YamlPathContext(
                CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
                "currentFile", "current.key", "value2"
            ),
            "rootFile", "root.key.path", 1
        )
        output1 = obj1.next_depth(input1)
        self.assertEqual(correct1, output1)


class TestTaskParsingContext(unittest.TestCase):
    def test_eq(self):
        obj1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        obj2 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value1"
            ),
            "taskName", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        obj2 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value2"
            ),
            "taskName", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_task_name(self):
        obj1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName1", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        obj2 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName2", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_task_type(self):
        obj1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType1", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        obj2 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType2", WhenSimpleTest("when"), TestFieldCreatorTask("name", ["field1"])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_when(self):
        obj1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType", WhenSimpleTest("when1"), TestFieldCreatorTask("name", ["field1"])
        )
        obj2 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType", WhenSimpleTest("when2"), TestFieldCreatorTask("name", ["field1"])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_prev_task(self):
        obj1 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name1", ["field1"])
        )
        obj2 = TaskParsingContext(
            YamlPathContext(
                CommandLineContext("input_dir", "output_dir", False, "config_file_path"),
                "currentFile", "current.key", "value"
            ),
            "taskName", "taskType", WhenSimpleTest("when"), TestFieldCreatorTask("name2", ["field1"])
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestConfigContext(unittest.TestCase):
    def test_eq(self):
        obj1 = ConfigContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        obj2 = ConfigContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_parent(self):
        obj1 = ConfigContext(
            CommandLineContext("inputDir1", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        obj2 = ConfigContext(
            CommandLineContext("inputDir2", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = ConfigContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        obj2 = ConfigContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            ["field1", "field3"],
            [
                Fileset(
                    "fileset",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_filesets(self):
        obj1 = ConfigContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset1",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        obj2 = ConfigContext(
            CommandLineContext("inputDir", "outputFilePath", False, "configFilePath"),
            ["field1", "field2"],
            [
                Fileset(
                    "fileset2",
                    ["field1", "field2"],
                    [InputFile("inputFile1", ["regex1"], [Sheet(["regex1"], True)])],
                    [TestFieldCreatorTask("task", ["field1", "field2"])]
                )
            ]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestSheet(unittest.TestCase):
    def test_eq(self):
        obj1 = Sheet(["regex1", "regex2"], False)
        obj2 = Sheet(["regex1", "regex2"], False)
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_regex(self):
        obj1 = Sheet(["regex1", "regex2"], False)
        obj2 = Sheet(["regex1", "regex3"], False)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_mandatory(self):
        obj1 = Sheet(["regex1", "regex2"], False)
        obj2 = Sheet(["regex1", "regex2"], True)
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestInputFile(unittest.TestCase):
    def test_eq(self):
        obj1 = InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])
        obj2 = InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])
        obj2 = InputFile("inputFile2", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_regex(self):
        obj1 = InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])
        obj2 = InputFile("inputFile1", ["regex1", "regex3"], [Sheet(["regex1", "regex2"], True)])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_sheet(self):
        obj1 = InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])
        obj2 = InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex3"], True)])
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)


class TestFileset(unittest.TestCase):
    def test_eq(self):
        obj1 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        obj2 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_name(self):
        obj1 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        obj2 = Fileset(
            "fileset2",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_fields(self):
        obj1 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        obj2 = Fileset(
            "fileset1",
            ["field1", "field3"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_input_files(self):
        obj1 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        obj2 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile2", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_tasks(self):
        obj1 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task1", ["field1", "field2"])]
        )
        obj2 = Fileset(
            "fileset1",
            ["field1", "field2"],
            [InputFile("inputFile1", ["regex1", "regex2"], [Sheet(["regex1", "regex2"], True)])],
            [TestFieldCreatorTask("task2", ["field1", "field2"])]
        )
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)
