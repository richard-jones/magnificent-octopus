from octopus.modules.es.testindex import ESTestCase
import json, time

from octopus.modules.infosys import models

RECORD_STRUCT = {
    "fields" : {
        "one" : {"coerce" : "unicode"}
    },
    "lists" : {
        "two" : {"contains" : "field", "coerce" : "unicode"}
    },
    "objects" : ["three"],
    "structs" : {
        "three" : {
            "fields" : {
                "four" : {"coerce" : "unicode"}
            }
        }
    }
}

RECORD_EXAMPLE = {
    "one" : "hello",
    "two" : ["another", "field"],
    "three" : {
        "four" : "object"
    }
}

ADMIN_STRUCT = {
    "fields" : {
        "alpha" : {"coerce" : "unicode"},
        "beta" : {"coerce" : "unicode"}
    }
}

ADMIN_EXAMPLE = {
    "alpha" : "hello",
    "beta" : "world"
}

INDEX_RULES = [
    {
        "index_field" : "first",
        "struct_args" : {"coerce" : "unicode"},
        "function" : {
            "name" : "add",
            "args" : [],
            "kwargs" : {}
        }
    },
    {
        "index_field" : "second",
        "struct_args" : {"coerce" : "unicode"},
        "function" : {
            "name" : "opath",
            "args" : ["$.record.three.four"],
            "kwargs" : {}
        }
    }
]

FULL_EXAMPLE = {
    "id" : "1234567890",
    "created_date" : "2001-01-01T00:00:00Z",
    "last_updated" : "2001-01-02T00:00:00Z",
    "record" : RECORD_EXAMPLE,
    "admin" : ADMIN_EXAMPLE,
    "index" : {}
}

class TestModels(ESTestCase):
    def setUp(self):
        super(TestModels, self).setUp()

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_01_construct(self):
        # first a basic construct
        ism = models.InfoSysModel()

        # now construct with some structs
        ism = models.InfoSysModel(record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT)

        # now construct with some structs and the index rules
        ism = models.InfoSysModel(record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES)

        # now same again, but with the data
        ism = models.InfoSysModel(record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, full=FULL_EXAMPLE)

        ism = models.InfoSysModel(record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, record=RECORD_EXAMPLE, admin=ADMIN_EXAMPLE)

        # test that properties bubble up to the parent objects
        ism = models.InfoSysModel(record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, full=FULL_EXAMPLE, expose_data=True)
        assert ism.admin.alpha == "hello"
        assert ism.record.one == "hello"

        # set the type
        ism = models.InfoSysModel(type="record1", record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, full=FULL_EXAMPLE, expose_data=True)

        print json.dumps(ism._struct, indent=2)
        print json.dumps(ism.data, indent=2)
        print json.dumps(ism._info_sys_properties, indent=2)

    def test_02_dao(self):
        # construct a full object
        ism = models.InfoSysModel(type="record1", record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, full=FULL_EXAMPLE, expose_data=True)

        # now save it
        ism.save(blocking=True)

        # now retrieve it
        ism2 = ism.pull(ism.id)
        assert ism2 is not None

        # now delete it
        ism.delete()
        ism3 = ism.pull(ism2.id)
        assert ism3 is None

    def test_03_query(self):
        # construct and save a full object
        ism = models.InfoSysModel(type="record1", record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, full=FULL_EXAMPLE, expose_data=True)
        ism.save(blocking=True)

        # try querying directly for the object
        res = ism.query(q={"query" : {"term" : {"admin.alpha.exact" : "hello"}}})
        assert len(res.get("hits", {}).get("hits", [])) == 1

        # now try scrolling over the results
        count = 0
        for res in ism.scroll(q={"query" : {"term" : {"admin.alpha.exact" : "hello"}}}):
            count += 1
        assert count == 1

        # do an object query
        res = ism.object_query(q={"query" : {"term" : {"admin.alpha.exact" : "hello"}}})
        assert len(res) == 1
        assert isinstance(res[0], models.InfoSysModel)

        # old fashioned query iteration
        count = 0
        for res in ism.iterate(q={"query" : {"term" : {"admin.alpha.exact" : "hello"}}}):
            count += 1
        assert count == 1

        # and iterate over all the results
        count = 0
        for res in ism.iterall():
            count += 1
        assert count == 1

        # last query: request a count of results for the query
        assert ism.count(q={"query" : {"term" : {"admin.alpha.exact" : "hello"}}}) == 1

        # now issue a delete by query
        ism.delete_by_query({"query" : {"term" : {"admin.alpha.exact" : "hello"}}})

        # wait to give it time to action
        time.sleep(2)

        # now check it has gone
        ism2 = ism.pull(ism.id)
        assert ism2 is None

    def test_04_prep(self):
        # construct a full object
        ism = models.InfoSysModel(type="record1", record_struct=RECORD_STRUCT, admin_struct=ADMIN_STRUCT, index_rules=INDEX_RULES, full=FULL_EXAMPLE, expose_data=True)

        # prep it, which will write the index components
        ism.prep()

        assert ism.index.second == [u"object"], ism.index.second
