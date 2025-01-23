import os

TESTASSETS_DIR = "testassets"
TESTYAML_NAME = "testyaml.yaml"
TESTYAML_PATH = os.path.join(TESTASSETS_DIR, TESTYAML_NAME)
TESTYAML_DICT = {
    "key1": {
        "subkey1": "value1",
        "subkey2": "value2"
    }
}
TESTLITERALLIST_NAME = "testliterallist.yaml"
TESTLITERALLIST_PATH = os.path.join(TESTASSETS_DIR, TESTLITERALLIST_NAME)
TESTLITERALLIST_LIST = [
    "value1", "value2"
]
TESTDICTLIST_NAME = "testdictlist.yaml"
TESTDICTLIST_PATH = os.path.join(TESTASSETS_DIR, TESTDICTLIST_NAME)
TESTDICTLIST_LIST = [
    {
        "subkey1": "value1",
        "subkey2": "value2"
    },
    {
        "subkey1": "value1",
        "subkey2": "value2"
    }
]
TESTTXT_NAME = "testtxt.txt"
TESTTXT_PATH = os.path.join(TESTASSETS_DIR, TESTTXT_NAME)
TESTTXT_TEXT = "This is a TEST."
BOTCHEDYAML_NAME = "botchedyaml.yaml"
BOTCHEDYAML_PATH = os.path.join(TESTASSETS_DIR, BOTCHEDYAML_NAME)
TESTCONFIG_NAME = "testconfig.yaml"
TESTCONFIG_PATH = os.path.join(TESTASSETS_DIR, TESTCONFIG_NAME)
TESTCONFIG_ILLEGALBLOCK_NAME = "testconfig_illegalblock.yaml"
TESTCONFIG_ILLEGALBLOCK_PATH = os.path.join(TESTASSETS_DIR, TESTCONFIG_ILLEGALBLOCK_NAME)
TESTFILESET_NAME = "testfileset.yaml"
TESTFILESET_PATH = os.path.join(TESTASSETS_DIR, TESTFILESET_NAME)
TESTINPUT_DIRNAME = "input"
TESTINPUT_PATH = os.path.join(TESTASSETS_DIR, TESTINPUT_DIRNAME)
TESTOUTPUT_DIRNAME = "output"
TESTOUTPUT_NAME = "output.csv"
TESTOUTPUT_PATH = os.path.join(TESTASSETS_DIR, TESTOUTPUT_DIRNAME, TESTOUTPUT_NAME)
TESTCSV_NAME = "testcsv.csv"
TESTCSV_PATH = os.path.join(TESTASSETS_DIR, TESTCSV_NAME)
TESTCSV_DUP_NAME = "testcsv_dup.csv"
TESTCSV_DUP_PATH = os.path.join(TESTASSETS_DIR, TESTCSV_DUP_NAME)
TESTXLS_NAME = "testxls.xlsx"
TESTXLS_PATH = os.path.join(TESTASSETS_DIR, TESTXLS_NAME)
TESTXLSENCRYPT_NAME = "testxlsencrypt.xlsx"
TESTXLSENCRYPT_PATH = os.path.join(TESTASSETS_DIR, TESTXLSENCRYPT_NAME)
