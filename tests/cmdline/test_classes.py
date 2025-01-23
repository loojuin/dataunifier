import unittest

from dataunifier.cmdline.classes import CommandLineContext


class TestCommandLineContext(unittest.TestCase):
    def test_eq(self):
        obj1 = CommandLineContext("input_dir", "output_file_path", True, "config_file_path")
        obj2 = CommandLineContext("input_dir", "output_file_path", True, "config_file_path")
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne_diff_input_dir(self):
        obj1 = CommandLineContext("input_dir1", "output_file_path", True, "config_file_path")
        obj2 = CommandLineContext("input_dir2", "output_file_path", True, "config_file_path")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_output_file_path(self):
        obj1 = CommandLineContext("input_dir", "output_file_path1", True, "config_file_path")
        obj2 = CommandLineContext("input_dir", "output_file_path2", True, "config_file_path")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_force(self):
        obj1 = CommandLineContext("input_dir", "output_file_path", True, "config_file_path")
        obj2 = CommandLineContext("input_dir", "output_file_path", False, "config_file_path")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_ne_diff_config_file_path(self):
        obj1 = CommandLineContext("input_dir", "output_file_path", True, "config_file_path1")
        obj2 = CommandLineContext("input_dir", "output_file_path", True, "config_file_path2")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_hash(self):
        obj1 = CommandLineContext("input_dir", "output_file_path", True, "config_file_path")
        correct1 = hash((obj1.input_dir, obj1.output_file_path, obj1.force, obj1.config_file_path))
        output1 = hash(obj1)
        self.assertEqual(correct1, output1)