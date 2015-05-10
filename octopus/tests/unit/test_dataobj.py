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

    def test_02_construct(self):
        struct = {
            "fields" : {
                "one" : {"coerce" : "unicode"}
            },
            "objects" : [
                "three", "four", "five"
            ],
            "lists" : {
                "six" : {"contains" : "whatever"},
                "seven" : {"contains" : "field", "coerce" : "integer"},
                "eight" : {"contains" : "object"},
                "nine" : {"contains" : "object"}
            },
            "required" : ["one"],
            "struct" : {
                # Note there's no structure for three, so it can be anything
                "four" : {
                    "fields" : {
                        "alpha" : {"coerce" : "integer"}
                    }
                },
                "nine" : {
                    "fields" : {
                        "beta" : {"coerce" : "integer"}
                    }
                }
            }
        }

        coerce = {
            "unicode" : dataobj.to_unicode(),
            "integer" : dataobj.to_int()
        }

        obj = { "one" : "hello" }
        new = dataobj.construct(obj, struct, coerce)
        assert new["one"] == u"hello"
        assert isinstance(new["one"], unicode)

        # try adding a disallowed field
        obj["two"]  = "world"

        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # try not providing a required field
        obj = {}
        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # try an unvalidated sub-object
        obj = {"one" : "hello"}
        obj["three"] = {"something" : "here"}
        new = dataobj.construct(obj, struct, coerce)
        assert new["three"]["something"] == "here"

        # and a validated sub-object
        obj["four"] = {"alpha" : "4"}
        new = dataobj.construct(obj, struct, coerce)
        assert new["four"]["alpha"] == 4

        # and a field that should be an object but isn't
        obj["five"] = "something here"
        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # a list where the list contains directive is broken
        del obj["five"]
        obj["six"] = ["6"]
        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # successfully coerce a list of field values
        del obj["six"]
        obj["seven"] = ["1", "1", "2", "3"]
        new = dataobj.construct(obj, struct, coerce)
        assert new["seven"] == [1, 1, 2, 3]

        # faile to coerce a list of field values
        obj["seven"] = ["a", "b", "walton-upon-thames"]
        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # list is supposed to contain an object but doesn't
        del obj["seven"]
        obj["eight"]  = ["not an object"]
        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # list contains an object but no validation required on its structure
        obj["eight"] = [{"an" : "object"}]
        new = dataobj.construct(obj, struct, coerce)
        assert new["eight"][0]["an"] == "object"

        # list contains an object which fails to validate
        obj["nine"] = [{"beta" : "whatever"}]
        with self.assertRaises(dataobj.DataStructureException):
            try:
                new = dataobj.construct(obj, struct, coerce)
            except dataobj.DataStructureException as e:
                print e.message
                raise e

        # list contains an object that does validate
        obj["nine"] = [{"beta" : 9}]
        new = dataobj.construct(obj, struct, coerce)
        assert new["nine"][0]["beta"] == 9