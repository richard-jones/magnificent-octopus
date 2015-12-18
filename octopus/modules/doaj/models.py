from octopus.lib import dataobj

BASE_ARTICLE_STRUCT = {
    "fields": {
        "id": {"coerce": "unicode"},                # Note that we'll leave these in for ease of use by the
        "created_date": {"coerce": "utcdatetime"},  # caller, but we'll need to ignore them on the conversion
        "last_updated": {"coerce": "utcdatetime"}   # to the real object
    },
    "objects": ["admin", "bibjson"],

    "structs": {

        "admin": {
            "fields": {
                "in_doaj": {"coerce": "bool", "get__default": False},
                "publisher_record_id": {"coerce": "unicode"},
                "upload_id": {"coerce": "unicode"}
            }
        },

        "bibjson": {
            "fields": {
                "title": {"coerce": "unicode"},
                "year": {"coerce": "unicode"},
                "month": {"coerce": "unicode"},
                "abstract": {"coerce": "unicode"}
            },
            "lists": {
                "identifier": {"contains": "object"},
                "link": {"contains": "object"},
                "author": {"contains": "object"},
                "keywords": {"coerce": "unicode", "contains": "field"},
                "subject": {"contains": "object"},
            },
            "objects": [
                "journal",
            ],
            "structs": {

                "identifier": {
                    "fields": {
                        "type": {"coerce": "unicode"},
                        "id": {"coerce": "unicode"}
                    }
                },

                "link": {
                    "fields": {
                        "type": {"coerce": "link_type"},
                        "url": {"coerce": "url"},
                        "content_type": {"coerce": "link_content_type"}
                    }
                },

                "author": {
                    "fields": {
                        "name": {"coerce": "unicode"},
                        "email": {"coerce": "unicode"},
                        "affiliation": {"coerce": "unicode"}
                    }
                },

                "journal": {
                    "fields": {
                        "start_page": {"coerce": "unicode"},
                        "end_page": {"coerce": "unicode"},
                        "volume": {"coerce": "unicode"},
                        "number": {"coerce": "unicode"},
                        "publisher": {"coerce": "unicode"},
                        "title": {"coerce": "unicode"},
                        "country": {"coerce": "unicode"}
                    },
                    "lists": {
                        "license": {"contains": "object"},
                        "language": {"coerce": "unicode", "contains": "field"}
                    },
                    "structs": {

                        "license": {
                            "fields": {
                                "title": {"coerce": "license"},
                                "type": {"coerce": "license"},
                                "url": {"coerce": "unicode"},
                                "version": {"coerce": "unicode"},
                                "open_access": {"coerce": "bool"},
                            }
                        }
                    }
                },

                "subject": {
                    "fields": {
                        "scheme": {"coerce": "unicode"},
                        "term": {"coerce": "unicode"},
                        "code": {"coerce": "unicode"}
                    }
                },
            }
        }
    }
}

class Journal(dataobj.DataObj):
    def __init__(self, raw=None):
        super(Journal, self).__init__(raw, expose_data=True)

    def all_issns(self):
        issns = []

        # get the issns from the identifiers record
        idents = self.bibjson.identifier
        if idents is not None:
            for ident in idents:
                if ident.type in ["pissn", "eissn"]:
                    issns.append(ident.id)

        hist = self.bibjson.history
        if hist is not None:
            for h in hist:
                idents = h.bibjson.identifier
                if idents is not None:
                    for ident in idents:
                        if ident.type in ["pissn", "eissn"]:
                            issns.append(ident.id)

        return issns

class Article(dataobj.DataObj):
    def __init__(self, raw=None):
        self._add_struct(BASE_ARTICLE_STRUCT)
        super(Article, self).__init__(raw, expose_data=True)