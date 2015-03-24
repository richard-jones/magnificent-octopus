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

    def by_doi(self, doi, page_size=10, page=1):
        return self.search('doi:"' + doi + '"', page_size=page_size, page=page)

    def search(self, search_string, page_size=10, page=1):
        # sort out the page size, which must be 10 or more
        if page_size < 10:
            page_size = 10

        # construct the URL that we'll search with
        url = self.api_base_url + "search/"
        quoted = quote(search_string, safe="/")
        url += quoted + "?page=" + quote(str(page)) + "&pageSize=" + quote(str(page_size)) + "&apiKey=" + quote(self.api_key)
        app.logger.info("Searching CORE with URL {x}".format(x=url))

        # make the request (this will handle re-tries if a 429 is received)
        resp = http.get(url, retry_codes=[429])

        # if we didn't get a response, raise an error
        if resp is None:
            app.logger.info("Was unable to communicate with CORE")
            raise CoreClientException("Was unable to communicate with CORE")

        # if a successful response, return the search result
        sr = None
        if resp.status_code == 200:
            app.logger.info("Got search results from CORE")
            sr = SearchResult(resp.json())
        elif resp.status_code == 400:
            app.logger.info("Got Not-OK status code from CORE: {x}".format(x=resp.status_code))
            resp.raise_for_status()
        elif resp.status_code == 401:
            app.logger.info("CORE API Key was invalid")
            resp.raise_for_status()
        elif resp.status_code == 429:
            app.logger.info("CORE API rate-limited us, and we retried several times before giving up")
            resp.raise_for_status()
        else:
            app.logger.info("Got unexpected status code from CORE: {x}".format(x=resp.status_code))
            resp.raise_for_status()

        return sr

class SearchResult(dataobj.DataObj):

    @property
    def status(self):
        return self._get_single("status", coerce=self._utf8_unicode())

    @property
    def records(self):
        return [SearchRecord(x) for x in self._get_list("data")]

class SearchRecord(dataobj.DataObj):

    @property
    def type(self):
        return self._get_single("type", coerce=self._utf8_unicode())

    @property
    def id(self):
        return self._get_single("id", coerce=self._utf8_unicode())