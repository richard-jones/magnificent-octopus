from copy import deepcopy
from octopus.lib import paths
import shutil

class SheetsFixtureFactory(object):

    @classmethod
    def test_spec(cls):
        return deepcopy(TEST_SPEC)

    @classmethod
    def incomplete_test_spec(cls):
        incomplete = deepcopy(TEST_SPEC)
        del incomplete["columns"][3]
        return incomplete

    @classmethod
    def complex_spec(cls):
        return deepcopy(COMPLEX_SPEC)

    @classmethod
    def simple_test_file_path(cls):
        return paths.rel2abs(__file__, "..", "resources", "test.csv")

    @classmethod
    def encoded_test_file_path(cls):
        return paths.rel2abs(__file__, "..", "resources", "test_encoded.csv")

    @classmethod
    def complex_test_file_path(cls):
        return paths.rel2abs(__file__, "..", "resources", "test_complex.csv")

    @classmethod
    def make_writable_source(cls):
        source = paths.rel2abs(__file__, "..", "resources", "test.csv")
        target = paths.rel2abs(__file__, "..", "resources", "test_read_write.csv")
        shutil.copyfile(source, target)
        return target

TEST_SPEC = {

    "columns" : [
        {
            "col_name" : "Column A",
            "trim" : True,
            "normalised_name" : "column_a",
            "default" : None,
            "coerce" : ["unicode"],
            "ignore_values" : []
        },
        {
            "col_name" : "Column B",
            "trim" : True,
            "normalised_name" : "column_b",
            "default" : None,
            "coerce" : ["unicode"],
            "ignore_values" : []
        },
        {
            "col_name" : "Column C",
            "trim" : True,
            "normalised_name" : "column_c",
            "default" : None,
            "coerce" : ["unicode"],
            "ignore_values" : []
        },
        {
            "col_name" : "Column D",
            "trim" : True,
            "normalised_name" : "column_d",
            "default" : None,
            "coerce" : ["unicode"],
            "ignore_values" : []
        }
    ]
}

COMPLEX_SPEC = {
    "columns" : [
        {
            "col_name" : "Column A",
            "normalised_name" : "column_a",
            "ignore_values" : ["Value 2"],
            "trim" : True
        },
        {
            "col_name" : "Column B",
            "coerce" : ["integer"],
        },
        {
            "col_name" : "Column C",
            "coerce" : ["integer", "unicode"],
            "default" : "100"
        },
        {
            "col_name" : "Column D",
            "ignore_values" : ["Ignore 1", "Ignore 2"]
        },
        {
            "col_name" : "Column E",
            "trim" : False
        }
    ]
}