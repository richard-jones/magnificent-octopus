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

        result = dictmerge.merge(source, target, rules, validate=True)

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

        result = dictmerge.merge(source, target, rules, validate=True)

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

        result = dictmerge.merge(source, target, rules, validate=True)

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

        result = dictmerge.merge(source, target, rules, validate=True)

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

        result = dictmerge.merge(source, target, rules, validate=True)

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

        result = dictmerge.merge(source, target, rules, validate=True)

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

        result = dictmerge.merge(source, target, rules, validate=True)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3
        assert result["four"] == [4.1, 4.3, 4.2]
        assert len(result["five"]) == 3
        assert [x.get("a") for x in result["five"]] == ["a1", "a3", "a2"]
        assert [x.get("b") for x in result["five"]] == ["b1", "b3", "b2"]
        assert len(result["six"]) == 3
        assert [(x.get("c"), x.get("d")[0].get("e"), x.get("d")[0].get("f"), x.get("g")) for x in result["six"]] == [("c1", "e1", "f1", "g1"), ("c3", "e3", "f3", None), ("c2", "e2", "f2", "g2")]

    def test_08_single_element_merge(self):
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
            ],
            "seven" : {
                "alpha" : "a"
            }
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
            ],
            "seven" : {
                "alpha" : "a1",
                "beta" : "b1"
            }
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
                },
                "seven" : {
                    "copy_if_missing" : ["beta"],
                    "override" : ["alpha"]
                }
            }
        }

        result = dictmerge.merge(source, target, rules, validate=True)

        assert result["one"] == 1
        assert result["two"] == [2, 2]
        assert result["three"] == 3
        assert result["four"] == [4.1, 4.3, 4.2]
        assert len(result["five"]) == 3
        assert [x.get("a") for x in result["five"]] == ["a1", "a3", "a2"]
        assert [x.get("b") for x in result["five"]] == ["b1", "b3", "b2"]
        assert len(result["six"]) == 3
        assert [(x.get("c"), x.get("d")[0].get("e"), x.get("d")[0].get("f"), x.get("g")) for x in result["six"]] == [("c1", "e1", "f1", "g1"), ("c3", "e3", "f3", None), ("c2", "e2", "f2", "g2")]
        assert result["seven"]["alpha"] == "a"
        assert result["seven"]["beta"] == "b1"

    def test_09_precedence(self):
        # This test covers the behaviour when fields appear in multiple rules, to ensure the precedence is correct.  These are the conditions this test looks at:
        #
        # copy_if_missing   override    list_append     merge       result
        # 0                 1           0               1           source
        # 0                 1           1               0           source
        # 0                 1           1               1           source
        # 1                 0           0               1           merged
        # 1                 0           1               0           appended
        # 1                 0           1               1           merged + appended
        # 1                 1           0               0           source
        # 1                 1           0               1           source
        # 1                 1           1               0           source
        # 1                 1           1               1           source

        source = {
            "one" : {
                "beta" : "b"
            },
            "two" : [2.1],
            "three" : [
                {
                    "alpha" : "a",
                    "beta" : "b"
                }
            ],
            "four" : {
                "alpha" : "a",
                "beta" : "b"
            },
            "five" : [5.1],
            "six" : [
                {
                    "alpha" : "a",
                    "beta" : "b"
                },
                {
                    "alpha" : "a1"
                }
            ],
            "seven" : 7.1,
            "eight" : {
                "alpha" : "a"
            },
            "nine" : [9.1, 9.2],
            "ten" : [
                {
                    "alpha" : "a",
                    "beta" : "b"
                }
            ]
        }
        target = {
            "one" : {
                "alpha" : "a",
            },
            "two" : [2.2],
            "three" : [
                {
                    "alpha" : "a",
                    "beta" : "b1"
                },
                {
                    "alpha" : "a1",
                    "beta" : "b2"
                }
            ],
            "four" : {
                "alpha" : "a1"
            },
            "five" : [5.1, 5.2],
            "six" : [
                {
                    "alpha" : "a",
                    "gamma" : "c"
                }
            ],
            "seven" : 7.2,
            "eight" : {
                "beta" : "b"
            },
            "nine" : [9.3, 9.4],
            "ten" : [
                {
                    "alpha" : "a",
                    "gamma" : "c"
                }
            ]
        }
        rules = {
            "copy_if_missing" : ["four", "five", "six", "seven", "eight", "nine", "ten"],
            "override" : ["one", "two", "three", "seven", "eight", "nine", "ten"],
            "list_append" : {
                "two" : { "dedupe" : False },
                "three" : {
                    "dedupe" : True,
                    "match" : [{
                        "must" : ["$.'alpha'"]
                    }]
                },
                "five" : { "dedupe" : False },
                "six" : {
                    "dedupe" : True,
                    "match" : [{
                        "must" : ["$.'alpha'"]
                    }]
                },
                "nine" : { "dedupe": False },
                "ten" : {
                    "dedupe" : True,
                    "match" : [{
                        "must" : ["$.'alpha'"]
                    }]
                }
            },
            "merge" : {
                "one" : {
                    "copy_if_missing" : ["alpha", "beta"]
                },
                "three" : {
                    "copy_if_missing" : ["alpha", "beta"]
                },
                "four" : {
                    "copy_if_missing" : ["alpha", "beta"]
                },
                "six" : {
                    "copy_if_missing" : ["alpha", "beta"]
                },
                "eight" : {
                    "copy_if_missing" : ["alpha", "beta"]
                },
                "ten" : {
                    "copy_if_missing" : ["alpha", "beta"]
                }
            }
        }

        result = dictmerge.merge(source, target, rules, validate=True)

        assert "beta" in result["one"]
        assert "alpha" not in result["one"]

        assert result["two"] == [2.1]

        assert len(result["three"]) == 1
        assert result["three"][0]["alpha"] == "a"
        assert result["three"][0]["beta"] == "b"

        assert result["four"]["alpha"] == "a1"
        assert result["four"]["beta"] == "b"

        assert result["five"] == [5.1, 5.2, 5.1]

        assert len(result["six"]) == 2
        assert result["six"][0]["alpha"] == "a"
        assert result["six"][0]["beta"] == "b"
        assert result["six"][0]["gamma"] == "c"
        assert result["six"][1]["alpha"] == "a1"

        assert result["seven"] == 7.1

        assert "alpha" in result["eight"]
        assert "beta" not in result["eight"]

        assert result["nine"] == [9.1, 9.2]

        assert len(result["ten"]) == 1
        assert "beta" in result["ten"][0]
        assert "gamma" not in result["ten"][0]

    def test_10_validate_rules(self):
        # 1. Rules aren't even a dict
        broken_rules = "whatever"
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {}
        dictmerge.validate_rules(fixed_rules)

        # 2. Unexpected key at the root
        broken_rules = {"whatever" : "hello"}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"copy_if_missing" : [], "override" : [], "list_append" : {}, "merge" : {}}
        dictmerge.validate_rules(fixed_rules)

        # 3. Incorrectly formatted copy_if_missing
        broken_rules = {"copy_if_missing" : "hello"}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        broken_rules = {"copy_if_missing" : [1]}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"copy_if_missing" : ["hello"]}
        dictmerge.validate_rules(fixed_rules)

        # 4. Incorrectly formatted override
        broken_rules = {"override" : "hello"}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        broken_rules = {"override" : [1]}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"override" : ["hello"]}
        dictmerge.validate_rules(fixed_rules)

        # 5. Incorrectly formatted list_append
        broken_rules = {"list_append" : "hello"}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {}}
        dictmerge.validate_rules(fixed_rules)

        # 6. Unexpected key in list_append
        broken_rules = {"list_append" : {27 : {}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {}}}
        dictmerge.validate_rules(fixed_rules)

        broken_rules = {"list_append" : {"field" : {"whatever" : "here"}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : []}}}
        dictmerge.validate_rules(fixed_rules)

        # 7. Invalid value in list_append dedupe field
        broken_rules = {"list_append" : {"field" : {"dedupe" : "yes", "match" : []}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : []}}}
        dictmerge.validate_rules(fixed_rules)

        # 8. Incorrectly formatted list_append match field
        broken_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : "hi"}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        broken_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : ["hi"]}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : []}}}
        dictmerge.validate_rules(fixed_rules)

        # 9. Unexpected key in list_append match directive
        broken_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"unexpected" : "key"}]}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"object_selector" : "$.hi", "must" : []}]}}}
        dictmerge.validate_rules(fixed_rules)

        # 10. Invalid object selector
        broken_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"object_selector" : ".hi", "must" : []}]}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"object_selector" : "$.hi", "must" : []}]}}}
        dictmerge.validate_rules(fixed_rules)

        # 11. Invalid must director/specifier
        broken_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"object_selector" : "$.hi", "must" : "there"}]}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        broken_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"object_selector" : "$.hi", "must" : ["there"]}]}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"list_append" : {"field" : {"dedupe" : True, "match" : [{"object_selector" : "$.hi", "must" : ["$.there"]}]}}}
        dictmerge.validate_rules(fixed_rules)

        # 12. Incorrectly specified merge rules
        broken_rules = {"merge" : "stuff"}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        broken_rules = {"merge" : {27 : {}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        broken_rules = {"merge" : {"field" : "whatever"}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"merge" : {"field" : {}}}
        dictmerge.validate_rules(fixed_rules)

        # 13. Nested merge rules also execute correctly
        broken_rules = {"merge" : {"field" : {"copy_if_missing" : "hello"}}}
        with self.assertRaises(dictmerge.RulesException):
            dictmerge.validate_rules(broken_rules)
        fixed_rules = {"merge" : {"field" : {"copy_if_missing" : ["hello"]}}}
        dictmerge.validate_rules(fixed_rules)