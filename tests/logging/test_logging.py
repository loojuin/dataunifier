import unittest

from dataunifier.logging import logging
from dataunifier.logging.constants import LOG_FILE_PATH_OPTION_STUB


class TestLogging(unittest.TestCase):
    def test_extract_log_file_path_specified(self):
        input1 = ["arg1", "arg2", f"{LOG_FILE_PATH_OPTION_STUB}log/file/path"]
        correct1 = "log/file/path"
        output1 = logging.extract_log_file_path(input1)
        self.assertEqual(correct1, output1)

    def test_extract_log_file_path_unspecified(self):
        input1 = ["arg1", "arg2", "arg3"]
        correct1 = None
        output1 = logging.extract_log_file_path(input1)
        self.assertEqual(correct1, output1)
