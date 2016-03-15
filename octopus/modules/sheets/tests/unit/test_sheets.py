from unittest import TestCase
from octopus.modules.sheets import sheets, commasep
from octopus.modules.sheets.tests import fixtures

class TestModels(TestCase):
    def setUp(self):
        super(TestModels, self).setUp()

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_01_read_simple_csv(self):
        spec = fixtures.SheetsFixtureFactory.test_spec()
        path = fixtures.SheetsFixtureFactory.simple_test_file_path()

        reader = commasep.CsvReader(path)
        obr = sheets.ObjectByRow(reader, spec)
        obr.read()

        dicts = [d for d in obr.dicts()]
        assert len(dicts) == 2

        two = False
        four = False
        for d in dicts:
            keys = d.keys()
            keys.sort()
            assert keys == ["column_a", "column_b", "column_c", "column_d"]
            values = d.values()
            values.sort()
            if values[0] == "Value A2":
                assert values == ["Value A2", "Value B2", "Value C2", "Value D2"]
                two = True
            else:
                assert values == ["Value A4", "Value B4", "Value C4", "Value D4"]
                four = True
        assert two
        assert four

        struct = obr.dataobj_struct()
        assert struct is not None
        fields = struct.get("fields").keys()
        fields.sort()
        assert fields == ["column_a", "column_b", "column_c", "column_d"]

    def test_02_read_encoded_csv(self):
        spec = fixtures.SheetsFixtureFactory.test_spec()
        path = fixtures.SheetsFixtureFactory.encoded_test_file_path()

        reader = commasep.CsvReader(path)
        obr = sheets.ObjectByRow(reader, spec)
        obr.read()

        dicts = [d for d in obr.dicts()]
        assert len(dicts) == 2

        two = False
        four = False
        for d in dicts:
            keys = d.keys()
            keys.sort()
            assert keys == ["column_a", "column_b", "column_c", "column_d"]
            values = d.values()
            values.sort()
            if values[0] == "Value A2":
                assert values == ["Value A2", "Value B2", "Value C2", "Value D2"]
                two = True
            else:
                assert values == ["Value A4", "Value B4", "Value C4", "Value D4"]
                four = True
        assert two
        assert four

        struct = obr.dataobj_struct()
        assert struct is not None
        fields = struct.get("fields").keys()
        fields.sort()
        assert fields == ["column_a", "column_b", "column_c", "column_d"]

    def test_03_complex_csv_read(self):
        spec = fixtures.SheetsFixtureFactory.complex_spec()
        path = fixtures.SheetsFixtureFactory.complex_test_file_path()

        reader = commasep.CsvReader(path)
        obr = sheets.ObjectByRow(reader, spec)
        obr.read()

        dicts = [d for d in obr.dicts()]
        assert len(dicts) == 2

        two = False
        three = False
        for d in dicts:
            keys = d.keys()
            keys.sort()
            assert keys == ["column_a", "column_b", "column_c", "column_d", "column_e"]

            if d.get("column_a") == "Value 1":
                two = True
                assert d.get("column_a") == "Value 1"
                assert d.get("column_b") == 1000
                assert d.get("column_c") == "2000"
                assert d.get("column_d") == None
                assert d.get("column_e") == "No Trim  "
            else:
                assert d.get("column_a") is None
                assert d.get("column_b") == 3000
                assert d.get("column_c") == "100"
                assert d.get("column_d") == None
                assert d.get("column_e") == "No Trim   "
                three = True

        assert two
        assert three