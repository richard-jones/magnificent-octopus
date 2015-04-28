import esprit
from esprit import mappings
from octopus.core import app
import json as jsonlib

class ESDAO(esprit.dao.DomainObject):
    __type__ = 'index'
    __conn__ = esprit.raw.Connection(app.config.get('ELASTIC_SEARCH_HOST'), app.config.get('ELASTIC_SEARCH_INDEX'))
    __es_version__ = app.config.get("ELASTIC_SEARCH_VERSION")

    @classmethod
    def mappings(cls):
        return {
            cls.__type__ : mappings.for_type(
                cls.__type__,
                    mappings.properties(mappings.type_mapping("location", "geo_point")),
                    mappings.dynamic_templates(
                    [
                        mappings.EXACT,
                    ]
                )
            )
        }

    @classmethod
    def delete_by_query(cls, query, conn=None, es_version="0.90.13"):
        esv = cls.__es_version__
        if esv is None:
            esv = es_version
        super(ESDAO, cls).delete_by_query(query, conn=conn, es_version=esv)

    def json(self):
        return jsonlib.dumps(self.data)

    def prep(self):
        pass

    def save(self, **kwargs):
        self.prep()
        super(ESDAO, self).save(**kwargs)

class QueryStringQuery(object):
    def __init__(self, qs, fro, psize):
        self.qs = qs
        self.fro = fro
        self.psize = psize

    def query(self):
        return {
            "query" :{
                "query_string" : {
                    "query" : self.qs
                }
            },
            "from" : self.fro,
            "size" : self.psize
        }