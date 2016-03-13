from unittest import TestCase
from octopus.lib import dictmerge

class TestDictMerge(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_copy_only(self):
        source = {
            "one" : 1,
            "two" : 2
        }
        target = {
            "two" : 3,
            "three" : 4
        }
        rules = {
            "copy_if_missing" : ["one", "two", "three"]
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == 3
        assert result["three"] == 4

    def test_02_override(self):
        source = {
            "one" : 1,
            "two" : 2
        }
        target = {
            "two" : 3,
            "three" : 4
        }
        rules = {
            "copy_if_missing" : ["one", "three"],
            "override" : ["two"]
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == 2
        assert result["three"] == 4

    def test_03_list_append_no_dedupe(self):
        source = {
            "one" : 1,
            "two" : [2],
            "three" : 3
        }
        target = {
            "two" : [2],
            "three" : 3.5
        }
        rules = {
            "copy_if_missing" : ["one", "two"],
            "override" : ["three"],
            "list_append" : {
                "two" : { "dedupe" : False }
            }
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3

    def test_04_list_append_dedupe_field(self):
        source = {
            "one" : 1,
            "two" : [2],
            "three" : 3,
            "four" : [4.1, 4.2]
        }
        target = {
            "two" : [2],
            "three" : 3.5,
            "four" : [4.1, 4.3]
        }
        rules = {
            "copy_if_missing" : ["one", "two"],
            "override" : ["three"],
            "list_append" : {
                "two" : { "dedupe" : False },
                "four" : { "dedupe" : True }
            }
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3
        assert result["four"] == [4.1, 4.3, 4.2]

    def test_05_list_append_dedupe_object(self):
        source = {
            "one" : 1,
            "two" : [2],
            "three" : 3,
            "four" : [4.1, 4.2],
            "five" : [
                {"a" : "a1", "b" : "b1"},
                {"a" : "a2", "b" : "b2"}
            ]
        }
        target = {
            "two" : [2],
            "three" : 3.5,
            "four" : [4.1, 4.3],
            "five" : [
                {"a" : "a1", "b" : "b1"},
                {"a" : "a3", "b" : "b3"}
            ]
        }
        rules = {
            "copy_if_missing" : ["one", "two"],
            "override" : ["three"],
            "list_append" : {
                "two" : { "dedupe" : False },
                "four" : { "dedupe" : True },
                "five" : {
                    "dedupe" : True,
                    "match" : [
                        {
                            "must" : ["$.a", "$.b"]
                        }
                    ]
                }
            }
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3
        assert result["four"] == [4.1, 4.3, 4.2]
        assert len(result["five"]) == 3
        assert [x.get("a") for x in result["five"]] == ["a1", "a3", "a2"]
        assert [x.get("b") for x in result["five"]] == ["b1", "b3", "b2"]

    def test_06_list_append_dedupe_deep_match(self):
        source = {
            "one" : 1,
            "two" : [2],
            "three" : 3,
            "four" : [4.1, 4.2],
            "five" : [
                {"a" : "a1", "b" : "b1"},
                {"a" : "a2", "b" : "b2"}
            ],
            "six" : [
                {"c" : "c1", "d" : [{"e" : "e1", "f" : "f1"}]},
                {"c" : "c2", "d" : [{"e" : "e2", "f" : "f2"}]}
            ]
        }
        target = {
            "two" : [2],
            "three" : 3.5,
            "four" : [4.1, 4.3],
            "five" : [
                {"a" : "a1", "b" : "b1"},
                {"a" : "a3", "b" : "b3"}
            ],
            "six" : [
                {"c" : "c1", "d" : [{"e" : "e1", "f" : "f1"}]},
                {"c" : "c3", "d" : [{"e" : "e3", "f" : "f3"}]}
            ]
        }
        rules = {
            "copy_if_missing" : ["one", "two"],
            "override" : ["three"],
            "list_append" : {
                "two" : { "dedupe" : False },
                "four" : { "dedupe" : True },
                "five" : {
                    "dedupe" : True,
                    "match" : [
                        {
                            "must" : ["$.'a'", "$.'b'"]
                        }
                    ]
                },
                "six" : {
                    "dedupe" : True,
                    "match" : [
                        {
                            "object_selector" : "$.'d'",
                            "must" : ["$.'e'", "$.'f'"]
                        }
                    ]
                }
            }
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3
        assert result["four"] == [4.1, 4.3, 4.2]
        assert len(result["five"]) == 3
        assert [x.get("a") for x in result["five"]] == ["a1", "a3", "a2"]
        assert [x.get("b") for x in result["five"]] == ["b1", "b3", "b2"]
        assert len(result["six"]) == 3
        assert [(x.get("c"), x.get("d")[0].get("e"), x.get("d")[0].get("f")) for x in result["six"]] == [("c1", "e1", "f1"), ("c3", "e3", "f3"), ("c2", "e2", "f2")]

    def test_07_list_append_dedupe_deep_merge(self):
        source = {
            "one" : 1,
            "two" : [2],
            "three" : 3,
            "four" : [4.1, 4.2],
            "five" : [
                {"a" : "a1", "b" : "b1"},
                {"a" : "a2", "b" : "b2"}
            ],
            "six" : [
                {"c" : "c1", "d" : [{"e" : "e1", "f" : "f1"}], "g" : "g1"},
                {"c" : "c2", "d" : [{"e" : "e2", "f" : "f2"}], "g" : "g2"}
            ]
        }
        target = {
            "two" : [2],
            "three" : 3.5,
            "four" : [4.1, 4.3],
            "five" : [
                {"a" : "a1", "b" : "b1"},
                {"a" : "a3", "b" : "b3"}
            ],
            "six" : [
                {"c" : "c1", "d" : [{"e" : "e1", "f" : "f1"}]},
                {"c" : "c3", "d" : [{"e" : "e3", "f" : "f3"}]}
            ]
        }
        rules = {
            "copy_if_missing" : ["one", "two"],
            "override" : ["three"],
            "list_append" : {
                "two" : { "dedupe" : False },
                "four" : { "dedupe" : True },
                "five" : {
                    "dedupe" : True,
                    "match" : [
                        {
                            "must" : ["$.'a'", "$.'b'"]
                        }
                    ]
                },
                "six" : {
                    "dedupe" : True,
                    "match" : [
                        {
                            "object_selector" : "$.'d'",
                            "must" : ["$.'e'", "$.'f'"]
                        }
                    ]
                }
            },
            "merge" : {
                "six" : {
                    "copy_if_missing" : ["g"]
                }
            }
        }

        result = dictmerge.merge(source, target, rules)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3
        assert result["four"] == [4.1, 4.3, 4.2]
        assert len(result["five"]) == 3
        assert [x.get("a") for x in result["five"]] == ["a1", "a3", "a2"]
        assert [x.get("b") for x in result["five"]] == ["b1", "b3", "b2"]
        assert len(result["six"]) == 3
        assert [(x.get("c"), x.get("d")[0].get("e"), x.get("d")[0].get("f"), x.get("g")) for x in result["six"]] == [("c1", "e1", "f1", "g1"), ("c3", "e3", "f3", None), ("c2", "e2", "f2", "g2")]

