from octopus.core import app
import esprit

class DOAJSearchClient(object):

    def __init__(self, search_base=None, query_endpoint=None, search_type=None, search_port=None):
        self.search_base = search_base if search_base else app.config.get("DOAJ_BASE_URL", "http://doaj.org")
        self.query_endpoint = query_endpoint if query_endpoint else app.config.get("DOAJ_QUERY_ENDPOINT", "query")
        self.search_type = search_type if search_type else app.config.get("DOAJ_SEARCH_TYPE", "journal,article")
        self.search_port = search_port if search_port else app.config.get("DOAJ_SEARCH_PORT", 80)

        # FIXME: we have turned off SSL verification for the moment, for convenience of working with the new
        # https-everywhere policy of the DOAJ
        self.conn = esprit.raw.Connection(self.search_base, self.query_endpoint, port=self.search_port, verify_ssl=False)

    def object_search(self, query):
        try:
            resp = esprit.raw.search(self.conn, type=self.search_type, query=query, method="GET")
            results = esprit.raw.unpack_result(resp)
            return results
        except:
            app.logger.info("Got exception talking to DOAJ query endpoint")
            return None

    def journals_by_issns(self, issns):
        if not isinstance(issns, list):
            issns = [issns]
        q = IssnQuery("journal", issns)
        return self.object_search(q.query())


class IssnQuery(object):
    def __init__(self, type, issn):
        self.type = type
        self.issn = issn

    def query(self):
        return {
            "query" : {
                "bool" : {
                    "must" : [
                        {"terms" : {"index.issn.exact" : self.issn}},
                        {"term" : {"_type" : self.type}}
                    ]
                }
            }
        }