from unittest import TestCase
from octopus.lib import dataobj

class TestImport(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_delete_with_prune(self):
        d = dataobj.DataObj()
        d._set_single("one.two", "value")
        d._set_single("one.three.four.five", "value")
        d._delete("one.three.four.five")
