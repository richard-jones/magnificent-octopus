from octopus.core import app
import urllib, requests
from lxml import etree

class EuropePMCException(Exception):
    def __init__(self, httpresponse, *args, **kwargs):
        super(EuropePMCException, self).__init__(*args, **kwargs)
        self.response = httpresponse

class EPMCFullTextException(Exception):
    def __init__(self, message, rawstring, *args, **kwargs):
        super(EPMCFullTextException, self).__init__(message, *args, **kwargs)
        self.raw = rawstring

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
        return cls.field_search("TITLE", title, fuzzy=True, page=page)

    @classmethod
    def field_search(cls, field, value, fuzzy=False, page=1):
        wrap = "\"" if not fuzzy else ""
        url = app.config.get("EPMC_REST_API") + "search/query=" + field + ":" + wrap + urllib.quote_plus(value, safe="/") + wrap
        url += "&resultType=core&format=json&page=" + urllib.quote_plus(str(page))

        print url

        resp = requests.get(url)
        if resp.status_code != 200:
            raise EuropePMCException(resp)

        j = resp.json()
        results = [EPMCMetadata(r) for r in j.get("resultList", {}).get("result", [])]
        return results

    @classmethod
    def fulltext(cls, pmcid):
        url = app.config.get("EPMC_REST_API") + pmcid + "/fullTextXML"
        print url
        resp = requests.get(url)
        if resp.status_code != 200:
            raise EuropePMCException(resp)
        return EPMCFullText(resp.text)

class EPMCMetadata(object):
    def __init__(self, raw):
        self.data = raw

class EPMCFullText(object):
    def __init__(self, raw):
        self.raw = raw
        try:
            self.xml = etree.fromstring(self.raw)
        except:
            raise EPMCFullTextException("Unable to parse XML", self.raw)
