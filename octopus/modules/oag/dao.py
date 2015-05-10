from octopus.modules.es import dao
from octopus.core import app
from datetime import datetime
from octopus.modules.oag import client as oag

class JobsDAO(dao.ESDAO):
    __type__ = app.config.get("OAGR_JOBS_ES_TYPE")

    @classmethod
    def has_due(cls):
        q = DueJobsQuery()
        counter = 0
        total = cls.count(q.query())
        for res in cls.iterate(q.query()):
            obj = cls.pull(res.id)
            state = oag.RequestState.from_json(obj.data)
            counter += 1
            yield state, counter, total

    @classmethod
    def job_statuses(cls):
        q = JobStatusQuery()
        for obj in cls.iterate(q.query(), wrap=False):
            yield obj.get("id"), obj.get("status")

    def state(self):
        return oag.RequestState.from_json(self.data)

    def prep(self):
        successes = len(self.data.get("success", []))
        errors = len(self.data.get("error", []))
        pending = len(self.data.get("pending", []))
        maxed = len(self.data.get("maxed", []))
        self.data["success_count"] = successes
        self.data["error_count"] = errors
        self.data["pending_count"] = pending
        self.data["maxed_count"] = maxed

class JobStatusQuery(object):
    def __init__(self):
        esv = app.config.get("ELASTIC_SEARCH_VERSION", "0.90.13")
        if esv.startswith("0"):
            self.fields = "fields"
        else:
            self.fields = "_source"
    def query(self):
        return {
            "query" : { "match_all" : {}},
            self.fields : ["id", "status"],
            "size" : 1000
        }

class DueJobsQuery(object):
    def __init__(self):
        esv = app.config.get("ELASTIC_SEARCH_VERSION", "0.90.13")
        if esv.startswith("0"):
            self.fields = "fields"
        else:
            self.fields = "_source"

    def query(self):
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "query" : {
                "bool" : {
                    "must" : [
                        {
                            "range" : {
                                "pending.due" : {
                                    "lte" : now
                                }
                            }
                        },
                        {
                            "range" : {
                                "start" : {
                                    "lte" : now
                                }
                            }
                        }
                    ]
                }
            },
            # FIXME: removed because of a bug in ES around date sorting
            # "sort" : [{"pending.due" : {"order" : "asc", "mode" : "min"}}],
            self.fields : [ "id" ],
            # "fields" : ["id"],
            "size" : 10000
        }