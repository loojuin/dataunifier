import os
import unittest

from dataunifier.cmdline.classes import CommandLineContext
from dataunifier.utils import confighelper
from dataunifier.config import constants
from dataunifier.config.classes import YamlPathContext
from dataunifier.common.exceptions import ConfigException
from tests.constants import TESTASSETS_DIR
from tests.constants import TESTYAML_PATH, TESTYAML_DICT, TESTYAML_NAME, BOTCHEDYAML_PATH, BOTCHEDYAML_NAME
from tests.constants import TESTLITERALLIST_NAME, TESTLITERALLIST_PATH, TESTLITERALLIST_LIST
from tests.constants import TESTDICTLIST_NAME, TESTDICTLIST_PATH, TESTDICTLIST_LIST
from tests.constants import TESTTXT_NAME, TESTTXT_TEXT


class TestConstructKey(unittest.TestCase):
    def test_string(self):
        key_path, next_key1 = "current.key", "new"
        correct1 = "current.key.new"
        output1 = confighelper.construct_key_path(key_path, next_key1)
        self.assertEqual(correct1, output1)

    def test_int(self):
        key_path, next_key1 = "current.key", 0
        correct1 = "current.key.0"
        output1 = confighelper.construct_key_path(key_path, next_key1)
        self.assertEqual(correct1, output1)

    def test_key_path_none(self):
        key_path, next_key1 = None, "key"
        correct1 = "key"
        output1 = confighelper.construct_key_path(key_path, next_key1)
        self.assertEqual(correct1, output1)

    def test_key_path_none_int(self):
        key_path, next_key1 = None, 0
        correct1 = "0"
        output1 = confighelper.construct_key_path(key_path, next_key1)
        self.assertEqual(correct1, output1)


class TestCheckInvalidKeys(unittest.TestCase):
    def test_no_invalid_keys(self):
        valid_keys = {"key1", "key2"}
        value = {
            "key1": "value1",
            "key2": "value2"
        }
        input1 = YamlPathContext(CommandLineContext("", "", False, ""), "", "", value)
        confighelper.check_invalid_keys(input1, valid_keys)

    def test_invalid_key_no_key_path(self):
        valid_keys = {"key1", "key2"}
        value = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, value
        )
        try:
            confighelper.check_invalid_keys(input1, valid_keys)
            self.fail()
        except ConfigException as e:
            correct1 = 'Unrecognized configuration keys in file "%s": "%s"' % (
                "currentFile", "key3"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_invalid_key_with_current_key(self):
        valid_keys = {"key1", "key2"}
        value = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.check_invalid_keys(input1, valid_keys)
            self.fail()
        except ConfigException as e:
            correct1 = 'Unrecognized configuration keys in object at "%s": "%s" (File "%s")' % (
                "current.key", "key3", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestParseConfigFile(unittest.TestCase):
    def test_successful(self):
        config_file_path = TESTYAML_PATH
        input1 = CommandLineContext("", "", False, config_file_path)
        correct1 = YamlPathContext(input1, config_file_path, None, TESTYAML_DICT)
        output1 = confighelper.parse_config_file(input1)
        self.assertEqual(correct1, output1)

    def test_file_not_found(self):
        config_file_path = os.path.join(TESTASSETS_DIR, "nonexistentfile.yaml")
        input1 = CommandLineContext("", "", False, config_file_path)
        try:
            confighelper.parse_config_file(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find configuration file "%s".' % config_file_path
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_parsing_error(self):
        config_file_path = BOTCHEDYAML_PATH
        input1 = CommandLineContext("", "", False, config_file_path)
        try:
            confighelper.parse_config_file(input1)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not interpret configuration file "%s". Details: ' % (config_file_path)
            output1 = e.message[0:len(correct1)]
            self.assertEqual(correct1, output1)


class TestGetLiteral(unittest.TestCase):
    def test_simple(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {"key1": "value1"}
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", "value1"
        )
        output1 = confighelper.get_literal(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference_input_dir(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, TESTTXT_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key.key1", TESTTXT_TEXT
        )
        output1 = confighelper.get_literal(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference_no_such_file(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, "nonexistent.txt")
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find text file "%s" (referenced in file "%s", key "%s")' % (
                os.path.join(TESTASSETS_DIR, "nonexistent.txt"),
                "currentFile", "current.key.key1"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_non_mandatory(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        output1 = confighelper.get_literal(input1, "key", False)
        self.assertIsNone(output1)

    def test_no_key_mandatory_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        try:
            confighelper.get_literal(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                "key", "current.key", "currentFile",
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_mandatory_no_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, {}
        )
        try:
            confighelper.get_literal(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                "key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_list(self):
        value = {
            "key1": ["string1", "string2"]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a single value, not a list or an object. ' \
                       '(File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_dict(self):
        value = {
            "key1": {
                "subkey1": "value1"
            }
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a single value, not a list or an object. ' \
                       '(File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestGetBoolean(unittest.TestCase):
    def test_bool(self):
        value = {
            "key1": True
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", True
        )
        output1 = confighelper.get_boolean(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_non_bool(self):
        value = {
            "key1": "true"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_boolean(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a boolean. (File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_non_mandatory(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        output1 = confighelper.get_boolean(input1, "key", False)
        self.assertIsNone(output1)

    def test_no_key_mandatory_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        try:
            confighelper.get_boolean(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                "key", "current.key", "currentFile",
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_mandatory_no_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, {}
        )
        try:
            confighelper.get_boolean(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                "key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_list(self):
        value = {
            "key1": ["string1", "string2"]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_boolean(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a single value, not a list or an object. ' \
                       '(File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_dict(self):
        value = {
            "key1": {
                "subkey1": "value1"
            }
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_boolean(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a single value, not a list or an object. ' \
                       '(File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestGetDict(unittest.TestCase):
    def test_simple(self):
        value = {
            "key1": {
                "subkey1": "value1"
            }
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", {
                "subkey1": "value1"
            }
        )
        output1 = confighelper.get_dict(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, TESTYAML_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), TESTYAML_PATH, None, TESTYAML_DICT
        )
        output1 = confighelper.get_dict(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference_no_such_file(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, "nonexistent.yaml")
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find YAML file "%s" (referenced in file "%s", key "%s")' % (
                os.path.join(TESTASSETS_DIR, "nonexistent.yaml"), "currentFile", "current.key.key1"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_file_reference_invalid_yaml(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, BOTCHEDYAML_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not interpret YAML file "%s" (referenced in file "%s", key "%s"). Details: ' % (
                os.path.join(TESTASSETS_DIR, BOTCHEDYAML_NAME), "currentFile", "current.key.key1"
            )
            output1 = e.message[0:len(correct1)]
            self.assertEqual(correct1, output1)

    def test_no_key_non_mandatory(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        output1 = confighelper.get_dict(input1, "key", False)
        self.assertIsNone(output1)

    def test_no_key_mandatory_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        try:
            confighelper.get_dict(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                "key", "current.key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_mandatory_no_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, {}
        )
        try:
            confighelper.get_dict(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                "key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_literal(self):
        value = {
            "key1": "value1"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be an object. (File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_list(self):
        value = {
            "key1": ["value1", "value2"]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be an object. (File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestGetList(unittest.TestCase):
    def test_literal(self):
        value = {
            "key1": "value1"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", [
                YamlPathContext(
                    CommandLineContext("", "", False, ""), "currentFile", "current.key.key1.0", "value1"
                )
            ]
        )
        output1 = confighelper.get_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_list(self):
        value = {
            "key1": ["value1"]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", [
                YamlPathContext(
                    CommandLineContext("", "", False, ""), "currentFile", "current.key.key1.0", "value1"
                )
            ]
        )
        output1 = confighelper.get_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference(self):
        input_dir = TESTASSETS_DIR
        clc = CommandLineContext(input_dir, "", False, "")
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, TESTLITERALLIST_NAME)
            )
        }
        input1 = YamlPathContext(
            clc, "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            clc, TESTLITERALLIST_PATH, None, [
                YamlPathContext(clc, TESTLITERALLIST_PATH, str(i), TESTLITERALLIST_LIST[i])
                for i in range(len(TESTLITERALLIST_LIST))
            ]
        )
        output1 = confighelper.get_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference_no_such_file(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, "nonexistent.yaml")
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find YAML file "%s" (referenced in file "%s", key "%s")' % (
                os.path.join(TESTASSETS_DIR, "nonexistent.yaml"), "currentFile", "current.key.key1"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_file_reference_invalid_yaml(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, BOTCHEDYAML_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not interpret YAML file "%s" (referenced in file "%s", key "%s"). Details: ' % (
                os.path.join(TESTASSETS_DIR, BOTCHEDYAML_NAME), "currentFile", "current.key.key1"
            )
            output1 = e.message[0:len(correct1)]
            self.assertEqual(correct1, output1)

    def test_no_key_non_mandatory(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        output1 = confighelper.get_list(input1, "key", False)
        self.assertIsNone(output1)

    def test_no_key_mandatory_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        try:
            confighelper.get_list(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                "key", "current.key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_mandatory_no_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, {}
        )
        try:
            confighelper.get_list(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                "key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestGetLiteralList(unittest.TestCase):
    def test_list(self):
        value = {
            "key1": ["value1", "value2"]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", [
                YamlPathContext(
                    CommandLineContext("", "", False, ""), "currentFile", "current.key.key1.0", "value1"
                ),
                YamlPathContext(
                    CommandLineContext("", "", False, ""), "currentFile", "current.key.key1.1", "value2"
                )
            ]
        )
        output1 = confighelper.get_literal_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_literal(self):
        value = {
            "key1": "value1"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key.key1", [
                YamlPathContext(
                    CommandLineContext("", "", False, ""), "currentFile", "current.key.key1.0", "value1"
                )
            ]
        )
        output1 = confighelper.get_literal_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, TESTLITERALLIST_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), TESTLITERALLIST_PATH, None, [
                YamlPathContext(
                    CommandLineContext(input_dir, "", False, ""), TESTLITERALLIST_PATH, str(i), TESTLITERALLIST_LIST[i]
                ) for i in range(len(TESTLITERALLIST_LIST))
            ]
        )
        output1 = confighelper.get_literal_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference_no_such_file(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, "nonexistent.yaml")
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find YAML file "%s" (referenced in file "%s", key "%s")' % (
                os.path.join(TESTASSETS_DIR, "nonexistent.yaml"), "currentFile", "current.key.key1"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_file_reference_invalid_yaml(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, BOTCHEDYAML_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not interpret YAML file "%s" (referenced in file "%s", key "%s"). Details: ' % (
                os.path.join(TESTASSETS_DIR, BOTCHEDYAML_NAME), "currentFile", "current.key.key1"
            )
            output1 = e.message[0:len(correct1)]
            self.assertEqual(correct1, output1)

    def test_no_key_non_mandatory(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        output1 = confighelper.get_literal_list(input1, "key", False)
        self.assertIsNone(output1)

    def test_no_key_mandatory_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        try:
            confighelper.get_literal_list(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                "key", "current.key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_mandatory_no_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, {}
        )
        try:
            confighelper.get_literal_list(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                "key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_dict(self):
        value = {
            "key1": {
                "subkey1": "value1"
            }
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a list of single values, not a list of objects. ' \
                       '(File "%s")' % (
                           "current.key.key1", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_dict_list(self):
        value = {
            "key1": [
                {
                    "subkey1": "value1"
                }
            ]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_literal_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a list of single values, not a list of objects. ' \
                       '(File "%s")' % (
                           "current.key.key1", "currentFile"
                       )
            output1 = e.message
            self.assertEqual(correct1, output1)


class TestGetDictList(unittest.TestCase):
    def test_dict_list(self):
        value = {
            "key1": [
                {
                    "subkey1": "value1"
                }
            ]
        }
        clc = CommandLineContext("", "", False, "")
        input1 = YamlPathContext(
            clc, "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            clc, "currentFile", "current.key.key1", [
                YamlPathContext(clc, "currentFile", "current.key.key1.0", {"subkey1": "value1"})
            ]
        )
        output1 = confighelper.get_dict_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_dict(self):
        value = {
            "key1": {
                "subkey1": "value1"
            }
        }
        clc = CommandLineContext("", "", False, "")
        input1 = YamlPathContext(
            clc, "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            clc, "currentFile", "current.key.key1", [
                YamlPathContext(clc, "currentFile", "current.key.key1.0", {"subkey1": "value1"})
            ]
        )
        output1 = confighelper.get_dict_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, TESTDICTLIST_NAME)
            )
        }
        clc = CommandLineContext(input_dir, "", False, "")
        input1 = YamlPathContext(
            clc, "currentFile", "current.key", value
        )
        correct1 = YamlPathContext(
            clc, TESTDICTLIST_PATH, None, [
                YamlPathContext(clc, TESTDICTLIST_PATH, str(i), TESTDICTLIST_LIST[i])
                for i in range(len(TESTDICTLIST_LIST))
            ]
        )
        output1 = confighelper.get_dict_list(input1, "key1", True)
        self.assertEqual(correct1, output1)

    def test_file_reference_no_such_file(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, "nonexistent.yaml")
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find YAML file "%s" (referenced in file "%s", key "%s")' % (
                os.path.join(TESTASSETS_DIR, "nonexistent.yaml"), "currentFile", "current.key.key1"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_file_reference_invalid_yaml(self):
        input_dir = TESTASSETS_DIR
        value = {
            "key1": "{{ %s:%s }}" % (
                constants.IMPORT_FILE_DIRECTIVE, os.path.join(constants.INPUT_DIR_PLACEHOLDER, BOTCHEDYAML_NAME)
            )
        }
        input1 = YamlPathContext(
            CommandLineContext(input_dir, "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not interpret YAML file "%s" (referenced in file "%s", key "%s"). Details: ' % (
                os.path.join(TESTASSETS_DIR, BOTCHEDYAML_NAME), "currentFile", "current.key.key1"
            )
            output1 = e.message[0:len(correct1)]
            self.assertEqual(correct1, output1)

    def test_no_key_non_mandatory(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        output1 = confighelper.get_dict_list(input1, "key", False)
        self.assertIsNone(output1)

    def test_no_key_mandatory_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", {}
        )
        try:
            confighelper.get_dict_list(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in object at key "%s" (File "%s")' % (
                "key", "current.key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_no_key_mandatory_no_current_key(self):
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", None, {}
        )
        try:
            confighelper.get_dict_list(input1, "key", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Could not find mandatory key "%s" in configuration file "%s".' % (
                "key", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_literal(self):
        value = {
            "key1": "value1"
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a list of objects. (File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)

    def test_literal_list(self):
        value = {
            "key1": ["value1"]
        }
        input1 = YamlPathContext(
            CommandLineContext("", "", False, ""), "currentFile", "current.key", value
        )
        try:
            confighelper.get_dict_list(input1, "key1", True)
            self.fail()
        except ConfigException as e:
            correct1 = 'Value of key "%s" is supposed to be a list of objects. (File "%s")' % (
                "current.key.key1", "currentFile"
            )
            output1 = e.message
            self.assertEqual(correct1, output1)
