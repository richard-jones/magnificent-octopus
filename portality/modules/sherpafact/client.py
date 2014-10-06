import urllib, requests, simplejson
from portality.core import app

class FactClientException(Exception):
    pass

class FactClient(object):
    QUERY_EXACT = "exact"
    QUERY_STARTS = "starts"
    QUERY_CONTAINS = "contains"

    def __init__(self, base_url=None, access_key=None):
        self.base_url = base_url if base_url is not None else app.config.get("FACT_BASE_URL")
        self.access_key = access_key if access_key is not None else app.config.get("ROMEO_API_KEY")

    def get_query_url(self, juliet_ids, journal_title=None, query_type=QUERY_EXACT, issn=None, output="json", trail=False):
        juliet_ids = self._normalise_juliet(juliet_ids)

        # check that we have enough information to build the request
        if juliet_ids is None or len(juliet_ids) == 0:
            raise FactClientException("At least one Juliet ID is required")

        if journal_title is None and issn is None:
            raise FactClientException("One of journal_title or issn must be specified (you specified neither)")

        if journal_title is not None and issn is not None:
            raise FactClientException("Only one of journal_title or issn can be specified.  Choose!")

        # build the base url
        url = self.base_url + "?ak=" + urllib.quote_plus(self.access_key)

        # append the juliet ids
        jids = ",".join(juliet_ids)
        url += "&juliet_id=" + urllib.quote_plus(jids)

        # append the journal title or the issn
        if journal_title is not None:
            url += "&journaltitle=" + urllib.quote_plus(journal_title) + "&querytype=" + urllib.quote_plus(query_type)
        else:
            url += "&issn=" + urllib.quote_plus(issn)

        # append the markup type
        url += "&markup=" + output

        # append whether to get the trail back
        if trail:
            url += "&trail=show"
        else:
            url += "&trail=hide"

        return url

    def raw_query(self, juliet_ids, journal_title=None, query_type=None, issn=None, output="json", trail=False):
        juliet_ids = self._normalise_juliet(juliet_ids)
        url = self.get_query_url(juliet_ids, journal_title, query_type, issn, output, trail)
        resp = requests.get(url)
        return resp, url

    def query(self, juliet_ids, journal_title=None, query_type=None, issn=None, output="json", trail=False):
        resp, url = self.raw_query(juliet_ids, journal_title, query_type, issn, output, trail)
        if resp.status_code != requests.codes.ok:
            raise FactClientException("Request to " + url + " produced status code " + str(resp.status_code))

        if output == "json":
            return self._read_json(resp)
        elif output == "xml":
            return Fact(resp.text)
        elif output == "php":
            return Fact(resp.text)

        return None

    def _read_json(self, resp):
        j = None
        source = resp.text
        while True:
            try:
                j = simplejson.loads(source)
                break
            except simplejson.JSONDecodeError as jde:
                if jde.pos and jde.message.startswith("Expecting ',' delimiter"):
                    source = source[:jde.pos] + "," + source[jde.pos:]
                else:
                    raise FactClientException("Unable to parse FACT API JSON")
        return FactJson(j)

    def _normalise_juliet(self, juliet_ids):
        if juliet_ids is not None:
            if not isinstance(juliet_ids, list):
                juliet_ids = [juliet_ids]
        else:
            return juliet_ids
        try:
            juliet_ids = [str(j) for j in juliet_ids]
            return juliet_ids
        except:
            raise FactClientException("Juliet IDs are malformed")

class Fact(object):
    def __init__(self, raw):
        self.raw = raw

class FactJson(Fact):
    pass