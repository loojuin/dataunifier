import os
import unittest

from dataunifier.utils import fileio
from dataunifier.common.exceptions import NoSuchDirectoryException, NoSuchFileException, NoFileMatchingRegexException, \
    YamlParsingException
from tests.constants import TESTASSETS_DIR, TESTTXT_PATH, TESTTXT_TEXT, TESTYAML_PATH, TESTYAML_DICT, TESTCSV_PATH


class TestGetFileNamesByRegex(unittest.TestCase):
    def test_successful(self):
        input1 = "^testcsv.*\\.csv$"
        correct1 = ["testcsv.csv", "testcsv_dup.csv"]
        output1 = fileio.get_file_names_by_regex(TESTASSETS_DIR, input1)
        self.assertEqual(correct1, output1)

    def test_no_such_dir(self):
        input1 = "nonexistent_directory"
        try:
            fileio.get_file_names_by_regex(input1, "some_regex")
            self.fail()
        except NoSuchDirectoryException as e:
            correct1 = input1
            correct2 = os.path.basename(input1)
            output1 = e.directory_path
            output2 = e.directory_name
            self.assertEqual(correct1, output1)
            self.assertEqual(correct2, output2)

    def test_no_file_matching_regex(self):
        input1 = "^nonexistent_file.txt$"
        try:
            fileio.get_file_names_by_regex(TESTASSETS_DIR, input1)
            self.fail()
        except NoFileMatchingRegexException as e:
            correct1 = TESTASSETS_DIR
            correct2 = input1
            output1 = e.directory
            output2 = e.regex
            self.assertEqual(correct1, output1)
            self.assertEqual(correct2, output2)


class TestCheckFileExistence(unittest.TestCase):
    def test_successful(self):
        input1 = os.path.join(TESTASSETS_DIR, "testcsv.csv")
        try:
            fileio.check_file_existence(input1)
        except NoSuchFileException:
            self.fail()

    def test_no_such_dir(self):
        input1 = os.path.join("nonexistent_directory", "testcsv.csv")
        try:
            fileio.check_file_existence(input1)
            self.fail()
        except NoSuchFileException as e:
            correct1 = input1
            correct2 = os.path.basename(input1)
            output1 = e.file_path
            output2 = e.file_name
            self.assertEqual(correct1, output1)
            self.assertEqual(correct2, output2)

    def test_no_such_file(self):
        input1 = os.path.join(TESTASSETS_DIR, "nonexistent_file.txt")
        try:
            fileio.check_file_existence(input1)
            self.fail()
        except NoSuchFileException as e:
            correct1 = input1
            correct2 = os.path.basename(correct1)
            output1 = e.file_path
            output2 = e.file_name
            self.assertEqual(correct1, output1)
            self.assertEqual(correct2, output2)


class TestCheckDirExistence(unittest.TestCase):
    def test_successful(self):
        input1 = TESTASSETS_DIR
        try:
            fileio.check_dir_existence(input1)
        except NoSuchDirectoryException:
            self.fail()

    def test_no_such_dir(self):
        input1 = "nonexistent_directory"
        try:
            fileio.check_dir_existence(input1)
            self.fail()
        except NoSuchDirectoryException as e:
            correct1 = input1
            correct2 = os.path.basename(input1)
            output1 = e.directory_path
            output2 = e.directory_name
            self.assertEqual(correct1, output1)
            self.assertEqual(correct2, output2)


class TestStripTrailingSep(unittest.TestCase):
    def test_changed(self):
        input1 = "%s%s" % (os.path.join("some", "directory"), os.path.sep)
        correct1 = os.path.join("some", "directory")
        output1 = fileio.strip_trailing_sep(input1)
        self.assertEqual(correct1, output1)

    def test_unchanged(self):
        input1 = os.path.join("some", "directory")
        correct1 = os.path.join("some", "directory")
        output1 = fileio.strip_trailing_sep(input1)
        self.assertEqual(correct1, output1)


class TestReadYamlFile(unittest.TestCase):
    def test_successful(self):
        input1 = TESTYAML_PATH
        correct1 = TESTYAML_DICT
        output1 = fileio.read_yaml_file(input1)
        self.assertEqual(correct1, output1)

    def test_parsing_error(self):
        input1 = os.path.join(TESTASSETS_DIR, "botchedyaml.yaml")
        try:
            fileio.read_yaml_file(input1)
            self.fail()
        except YamlParsingException:
            pass


class TestReadTextFile(unittest.TestCase):
    def test_successful(self):
        input1 = TESTTXT_PATH
        correct1 = TESTTXT_TEXT
        output1 = fileio.read_text_file(input1)
        self.assertEqual(correct1, output1)


class TestGetExtension(unittest.TestCase):
    def test_simple(self):
        input1 = os.path.join("some", "file", "path.ext")
        correct1 = "ext"
        output1 = fileio.get_extension(input1)
        self.assertEqual(correct1, output1)

    def test_no_extension(self):
        input1 = os.path.join("some", "file", "path")
        correct1 = "path"
        output1 = fileio.get_extension(input1)
        self.assertEqual(correct1, output1)


class TestCountRows(unittest.TestCase):
    def test_simple(self):
        input1 = TESTCSV_PATH
        correct1 = 2
        output1 = fileio.count_rows(input1)
        self.assertEqual(correct1, output1)
