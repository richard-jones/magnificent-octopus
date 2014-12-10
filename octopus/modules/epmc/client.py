from octopus.core import app
from octopus.lib import dataobj
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

class EPMCMetadata(dataobj.DataObj):
    def __init__(self, raw):
        self.data = raw

    @property
    def pmcid(self):
        return self._get_single("pmcid", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def pmid(self):
        return self._get_single("pmid", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def doi(self):
        return self._get_single("doi", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def in_epmc(self):
        return self._get_single("inEPMC", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def is_oa(self):
        return self._get_single("isOpenAccess", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def issn(self):
        return self._get_single("journalInfo.journal.issn", self._utf8_unicode(), allow_coerce_failure=False)

class EPMCFullText(object):
    def __init__(self, raw):
        self.raw = raw
        try:
            self.xml = etree.fromstring(self.raw)
        except:
            raise EPMCFullTextException("Unable to parse XML", self.raw)

    @property
    def is_aam(self):
        manuscripts = self.xml.xpath("//article-id[@pub-id-type='manuscript']")
        return len(manuscripts) > 0

    def get_licence_details(self):
        # get the licence type
        l = self.xml.xpath("//license")
        if len(l) > 0:
            l = l[0]
        type = l.get("license-type")
        url = l.get("{http://www.w3.org/1999/xlink}href")

        # get the paragraph describing the licence
        para = self.xml.xpath("//license/license-p")
        if len(para) > 0:
            para = para[0]
        p = etree.tostring(para)

        return type, url, p