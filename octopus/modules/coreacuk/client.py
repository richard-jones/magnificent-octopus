from octopus.core import app
from octopus.lib import http, dataobj
import urllib

def quote(s, **kwargs):
    try:
        return urllib.quote_plus(s, **kwargs)
    except:
        pass

    try:
        utf = s.encode("utf-8")
        return urllib.quote(utf, **kwargs)
    except:
        return None

class CoreClientException(Exception):
    pass

class Core(object):
    def __init__(self, api_key=None, api_base_url=None):
        self.api_key = api_key if api_key is not None else app.config.get("CORE_API_KEY")
        self.api_base_url = api_base_url if api_base_url is not None else app.config.get("CORE_API_BASE_URL")

    def search(self, search_criteria, count=10, offset=0):
        # construct the URL that we'll search with
        url = self.api_base_url + "search/"
        quoted = quote(search_criteria)
        url += quoted + "?format=json&count=" + quote(str(count)) + "&offset=" + quote(str(offset)) + "&api_key=" + quote(self.api_key)
        app.logger.info("Searching CORE with URL {x}".format(x=url))

        # make the request
        resp = http.get(url)

        # if we didn't get a response, raise an error
        if resp is None:
            app.logger.info("Was unable to communicate with CORE")
            raise CoreClientException("Was unable to communicate with CORE")

        if resp.status_code not in [200, 204]:
            app.logger.info("Got Not-OK status code from CORE: {x}".format(x=resp.status_code))
            resp.raise_for_status()

        if resp.status_code == 200:
            app.logger.info("Got search results from CORE")
            sr = SearchResult(resp.json())
        else:
            app.logger.info("Got no results from CORE - returning empty result set")
            sr = SearchResult()

        return sr

class SearchResult(dataobj.DataObj):

    @property
    def total_hits(self):
        lrs = self._get_single("ListRecords", default=[])
        if len(lrs) > 0:
            return int(lrs[0].get("total_hits"))
        else:
            return 0

    @property
    def records(self):
        lrs = self._get_single("ListRecords", default=[])
        if len(lrs) > 1:
            return [Record(x.get("record", {})) for x in lrs[1:]]
        else:
            return []

class Record(dataobj.DataObj):
    pass