from octopus.core import app
from octopus.lib import http
import urllib, string
from lxml import etree
from octopus.modules.epmc import models
from octopus.modules.epmc.queries import QueryBuilder

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

def to_keywords(s):
    # FIXME: this method does not strip stop words - investigations into that indicate that as a natural language
    # processing thing, the libraries required to do it are awkward and overblown for our purposes.

    # translate out all of the punctuation
    exclude = set(string.punctuation)
    raw = ''.join(ch if ch not in exclude else " " for ch in s)

    # normalise the spacing
    return " ".join([x for x in raw.split(" ") if x != ""])

class EuropePMCException(Exception):
    def __init__(self, httpresponse=None, *args, **kwargs):
        super(EuropePMCException, self).__init__(*args, **kwargs)
        self.response = httpresponse

class EuropePMC(object):
    @classmethod
    def get_by_pmcid(cls, pmcid, page=1):
        return cls.field_search("PMCID", pmcid, page=page)

    @classmethod
    def get_by_pmid(cls, pmid, page=1):
        return cls.field_search("EXT_ID", pmid, page=page)

    @classmethod
    def get_by_doi(cls, doi, page=1):
        return cls.field_search("DOI", doi, page=page)

    @classmethod
    def title_exact(cls, title, page=1):
        return cls.field_search("TITLE", title, page=page)

    @classmethod
    def title_approximate(cls, title, page=1):
        nt = to_keywords(title)
        return cls.field_search("TITLE", nt, fuzzy=True, page=page)

    @classmethod
    def field_search(cls, field, value, fuzzy=False, page=1, page_size=25):
        qb = QueryBuilder()
        qb.add_string_field(field, value, fuzzy)
        return cls.query(qb.to_url_query_param(), page=page, page_size=page_size)

    @classmethod
    def field_search_iterator(cls, field, value, fuzzy=False, page=1, page_size=25):
        qb = QueryBuilder()
        qb.add_string_field(field, value, fuzzy)
        return cls.iterate(qb.to_url_query_param(), page=page, page_size=page_size)

    @classmethod
    def complex_search(cls, query_builder, page=1, page_size=25):
        return cls.query(query_builder.to_url_query_param(), page=page, page_size=page_size)

    @classmethod
    def complex_search_iterator(cls, query_builder, page_size=1000):
        return cls.iterate(query_builder.to_url_query_param(), page_size=page_size)

    @classmethod
    def iterate(cls, query_string, page_size=1000):
        page = 1
        while True:
            results = cls.query(query_string, page=page, page_size=page_size)
            if len(results) == 0:
                break
            for r in results:
                yield r
            page += 1

    @classmethod
    def query(cls, query_string, page=1, page_size=25):
        quoted = quote(query_string, safe="/")
        qpage = quote(str(page))
        qsize = quote(str(page_size))
        if qsize is None or qpage is None or quoted is None:
            raise EuropePMCException(None, "unable to url escape the string")

        url = app.config.get("EPMC_REST_API") + "search/query=" + query_string
        url += "&resultType=core&format=json&page=" + qpage + "&pageSize=" + qsize
        app.logger.debug("Requesting EPMC metadata from " + url)

        resp = http.get(url)
        if resp is None:
            raise EuropePMCException(message="could not get a response from EPMC")
        if resp.status_code != 200:
            raise EuropePMCException(resp)

        try:
            j = resp.json()
        except:
            raise EuropePMCException(message="could not decode JSON from EPMC response")

        results = [models.EPMCMetadata(r) for r in j.get("resultList", {}).get("result", [])]
        return results

    @classmethod
    def fulltext(cls, pmcid):
        url = app.config.get("EPMC_REST_API") + pmcid + "/fullTextXML"
        app.logger.debug("Searching for Fulltext at " + url)
        resp = http.get(url)
        if resp is None:
            raise EuropePMCException(message="could not get a response for fulltext from EPMC")
        if resp.status_code != 200:
            raise EuropePMCException(resp)
        return EPMCFullText(resp.text)

class EPMCFullText(models.JATS):
    """
    For backwards compatibility - don't add any methods here
    """
    pass

