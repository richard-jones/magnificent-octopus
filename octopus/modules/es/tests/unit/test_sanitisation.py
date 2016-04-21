from unittest import TestCase
from octopus.modules.es import sanitise

class TestModels(TestCase):
    def setUp(self):
        super(TestModels, self).setUp()

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_01_basic_success(self):
        query = {
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : 9
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT)

        assert sane == query

    def test_02_no_query(self):
        query = {
            "size" : 10,
            "from" : 9
        }

        with self.assertRaises(sanitise.QuerySanitisationException):
            sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT)

    def test_03_disallowed_fields(self):
        query = {
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9,
            "random" : "field",
            "aggs" : {},         # without the type_field_map this should be stripped out
            "sort" : []         # without the type_field_map this should be stripped out
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT)

        expected = {
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9
        }

        assert sane == expected

    def test_04_aggregations_success(self):
        query = {
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9,
            "aggs" : {
                "first" : {
                    "terms" : {"field" : "aaaa"}
                },
                "second" : {
                    "terms" : {"field" : "bbbb"},
                    "aggs" : {
                        "aleph" : {
                            "date_histogram" : {"field" : "dddd"}
                        }
                    }
                },
                "third" : {
                    "date_histogram" : {"field" : "cccc"}
                }
            }
        }

        type_field_map = {
            "terms" : {
                "aaaa" : {
                    "aggs" : False
                },
                "bbbb" : {
                    "aggs" : True,
                    "type_field_map" : {
                        "date_histogram" : {
                            "dddd" : {
                                "aggs" : False
                            }
                        }
                    }
                }
            },
            "date_histogram" : {
                "cccc" : {
                    "aggs" : False
                }
            }
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT, aggs_type_field_map=type_field_map)

        assert sane == query

    def test_05_aggregations_stripped(self):
        query = {
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9,
            "aggregations" : {
                "first" : {
                    "terms" : {"field" : "aaaa"},
                    "aggregations" : {
                        "alpha" : {
                            "date_histogram" : {"field" : "eeee"}
                        }
                    }
                },
                "second" : {
                    "terms" : {"field" : "bbbb"},
                    "aggregations" : {
                        "aleph" : {
                            "date_histogram" : {"field" : "dddd"}
                        }
                    }
                },
                "third" : {
                    "date_histogram" : {"field" : "cccc"}
                }
            }
        }

        type_field_map = {
            "terms" : {
                "aaaa" : {
                    "aggs" : False
                },
                "bbbb" : {
                    "aggs" : True,
                    "type_field_map" : {
                        "date_histogram" : {
                            "ffff" : {
                                "aggs" : False
                            }
                        }
                    }
                }
            }
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT, aggs_type_field_map=type_field_map)

        expected = {
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9,
            "aggregations" : {
                "first" : {
                    "terms" : {"field" : "aaaa"},
                },
                "second" : {
                    "terms" : {"field" : "bbbb"},
                }
            }
        }

        assert sane == expected

    def test_06_coerce_fail(self):
        query = {
            "query" : {"match_all" : {}},
            "size" : "ten",
            "from" : 9
        }

        with self.assertRaises(sanitise.QuerySanitisationException):
            sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT)

        query = {
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : "nine"
        }

        with self.assertRaises(sanitise.QuerySanitisationException):
            sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT)

    def test_07_unfiltered(self):
        query = {
            "query" : {"bool" : {"must" : [{"term" : {"index.field" : "one"}}]}},
            "size" : "ten",
            "from" : 9
        }

        with self.assertRaises(sanitise.QuerySanitisationException):
            sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT)

    def test_08_sources(self):
        query = {
            "source" : {
                "includes" : ["whatever"]
            },
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : 9
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT, source_includes=["id", "created_date", "last_updated"])

        expected = {
            "source" : {
                "includes" : ["id", "created_date", "last_updated"]
            },
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : 9
        }

        assert sane == expected

    def test_09_sorting(self):
        query = {
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : 9,
            "sort" : [
                {"one" : {"order" : "asc"}},
                {"two" : {"order" : "desc"}},
                {"three" : {"order" : "asc"}}
            ]
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT, sortable=["one", "three"])

        expected = {
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : 9,
            "sort" : [
                {"one" : {"order" : "asc"}},
                {"three" : {"order" : "asc"}}
            ]
        }

        assert sane == expected

        query = {
            "query" : {"match_all" : {}},
            "size" : 10,
            "from" : 9,
            "sort" : [
                "field", "here"
            ]
        }

        with self.assertRaises(sanitise.QuerySanitisationException):
            sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT, sortable=["field", "here"])

    def test_10_all_together(self):
        query = {
            "source" : {
                "includes" : ["whatever"]
            },
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9,
            "random" : "field",
            "aggregations" : {
                "first" : {
                    "terms" : {"field" : "aaaa"},
                    "aggs" : {
                        "alpha" : {
                            "date_histogram" : {"field" : "eeee"}
                        }
                    }
                },
                "second" : {
                    "terms" : {"field" : "bbbb"},
                    "aggs" : {
                        "aleph" : {
                            "date_histogram" : {"field" : "dddd"}
                        }
                    }
                },
                "third" : {
                    "date_histogram" : {"field" : "cccc"}
                }
            },
            "sort" : [
                {"one" : {"order" : "asc"}},
                {"two" : {"order" : "desc"}},
                {"three" : {"order" : "asc"}}
            ]
        }

        type_field_map = {
            "terms" : {
                "aaaa" : {
                    "aggs" : False
                },
                "bbbb" : {
                    "aggs" : True,
                    "type_field_map" : {
                        "date_histogram" : {
                            "ffff" : {
                                "aggs" : False
                            }
                        }
                    }
                }
            }
        }

        sane = sanitise.sanitise(query, sanitise.EDGES_STRUCT,
                                 source_includes=["id", "created_date", "last_updated"],
                                 sortable=["one", "three"],
                                 aggs_type_field_map=type_field_map)

        expected = {
            "source" : {
                "includes" : ["id", "created_date", "last_updated"]
            },
            "query" : {"filtered" : {"filter" : {"terms" : {"index.field" : ["one", "two"]}}}},
            "size" : 10,
            "from" : 9,
            "aggregations" : {
                "first" : {
                    "terms" : {"field" : "aaaa"},
                },
                "second" : {
                    "terms" : {"field" : "bbbb"},
                }
            },
            "sort" : [
                {"one" : {"order" : "asc"}},
                {"three" : {"order" : "asc"}}
            ]
        }

        assert sane == expected