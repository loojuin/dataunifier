import os
import unittest

from dataunifier.cmdline import cmdline
from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.cmdline.constants import INPUT_DIR_OPTION_STUB, DEFAULT_INPUT_DIR, OUTPUT_OPTION_STUB, \
    DEFAULT_OUTPUT_FILE_PATH, FORCE_OPTION
from dataunifier.common.exceptions import SyntaxException, CommandLineException

from tests import constants as testconstants


class TestExtractOptions(unittest.TestCase):
    def test_with_options(self):
        input1 = ["run.py", f"{FORCE_OPTION}", "--config=path/to/config", "input_dir", "output_file"]
        correct1 = (["run.py", "input_dir", "output_file"], {f"{FORCE_OPTION}", "--config=path/to/config"})
        output1 = cmdline.extract_options(input1)
        self.assertEqual(correct1, output1)

    def test_without_options(self):
        input1 = ["run.py", "input_dir", "output_file"]
        correct1 = (["run.py", "input_dir", "output_file"], set())
        output1 = cmdline.extract_options(input1)
        self.assertEqual(correct1, output1)


class TestGetInputDir(unittest.TestCase):
    def test_specified(self):
        input1 = {f"{FORCE_OPTION}", f"{INPUT_DIR_OPTION_STUB}path/to/input/dir", "--some-other-option=no"}
        correct1 = "path/to/input/dir"
        output1 = cmdline.get_input_directory(input1)
        self.assertEqual(correct1, output1)

    def test_unspecified(self):
        input1 = {f"{FORCE_OPTION}", "--some-other-option=no"}
        correct1 = DEFAULT_INPUT_DIR
        output1 = cmdline.get_input_directory(input1)
        self.assertEqual(correct1, output1)


class TestGetOutputFile(unittest.TestCase):
    def test_specified(self):
        input1 = {f"{FORCE_OPTION}", f"{OUTPUT_OPTION_STUB}path/to/output.csv", "--some-other-option=no"}
        correct1 = "path/to/output.csv"
        output1 = cmdline.get_output_file(input1)
        self.assertEqual(correct1, output1)

    def test_unspecified(self):
        input1 = {f"{FORCE_OPTION}", "--some-other-option=no"}
        correct1 = DEFAULT_OUTPUT_FILE_PATH
        output1 = cmdline.get_output_file(input1)
        self.assertEqual(correct1, output1)


class TestGetContext(unittest.TestCase):
    def test_successful_with_options(self):
        input1 = [
            "run.py",
            f"{FORCE_OPTION}",
            f"{INPUT_DIR_OPTION_STUB}{testconstants.TESTINPUT_PATH}",
            f"{OUTPUT_OPTION_STUB}{testconstants.TESTOUTPUT_PATH}",
            testconstants.TESTCONFIG_PATH,
        ]
        correct1 = CommandLineContext(
            testconstants.TESTINPUT_PATH,
            testconstants.TESTOUTPUT_PATH,
            True,
            testconstants.TESTCONFIG_PATH,
        )
        output1 = cmdline.get_context(input1)
        self.assertEqual(correct1, output1)

    def test_successful_without_options(self):
        input1 = ["run.py", testconstants.TESTCONFIG_PATH]
        correct1 = CommandLineContext(
            DEFAULT_INPUT_DIR,
            DEFAULT_OUTPUT_FILE_PATH,
            False,
            testconstants.TESTCONFIG_PATH,
        )
        output1 = cmdline.get_context(input1)
        self.assertEqual(correct1, output1)

    def test_syntax_error_with_options(self):
        input1 = [
            "run.py",
            f"{FORCE_OPTION}",
            f"{INPUT_DIR_OPTION_STUB}{testconstants.TESTINPUT_PATH}",
            f"{OUTPUT_OPTION_STUB}{testconstants.TESTOUTPUT_PATH}"
        ]
        try:
            cmdline.get_context(input1)
            self.fail()
        except SyntaxException as e:
            correct1 = "Incorrect number of arguments."
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_syntax_error_without_options(self):
        input1 = ["run.py"]
        try:
            cmdline.get_context(input1)
            self.fail()
        except SyntaxException as e:
            correct1 = "Incorrect number of arguments."
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_such_input_dir(self):
        input1 = [
            "run.py",
            f"{FORCE_OPTION}",
            f"{INPUT_DIR_OPTION_STUB}nonexistent",
            f"{OUTPUT_OPTION_STUB}{testconstants.TESTOUTPUT_PATH}",
            testconstants.TESTCONFIG_PATH
        ]
        try:
            cmdline.get_context(input1)
            self.fail()
        except CommandLineException as e:
            correct1 = 'Could not find input directory "nonexistent".'
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_output_dir(self):
        input1 = [
            "run.py",
            f"{FORCE_OPTION}",
            f"{INPUT_DIR_OPTION_STUB}{testconstants.TESTINPUT_PATH}",
            f"{OUTPUT_OPTION_STUB}{os.path.join('nonexistent', 'file.csv')}",
            testconstants.TESTCONFIG_PATH,
        ]
        try:
            cmdline.get_context(input1)
            self.fail()
        except CommandLineException as e:
            correct1 = 'Directory for output file "nonexistent" does not exist.'
            output1 = e.message
            self.assertEqual(correct1, output1)
