from octopus.core import app
from octopus.lib import dataobj, http
import urllib, string
from lxml import etree

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
    def __init__(self, *args, **kwargs):
        httpresponse = kwargs.get("httpresponse")
        if httpresponse is not None:
            del kwargs["httpresponse"]
        super(EuropePMCException, self).__init__(*args)
        self.response = httpresponse

class EPMCFullTextException(Exception):
    def __init__(self, message, rawstring, *args, **kwargs):
        super(EPMCFullTextException, self).__init__(message, *args)
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
        nt = to_keywords(title)
        return cls.field_search("TITLE", nt, fuzzy=True, page=page)

    @classmethod
    def field_search(cls, field, value, fuzzy=False, page=1):
        wrap = "\"" if not fuzzy else ""
        quoted = quote(value, safe="/")
        qpage = quote(str(page))
        if quoted is None or qpage is None:
            raise EuropePMCException(None, "unable to url escape the string")

        url = app.config.get("EPMC_REST_API") + "search/query=" + field + ":" + wrap + quoted + wrap
        url += "&resultType=core&format=json&page=" + qpage
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

        results = [EPMCMetadata(r) for r in j.get("resultList", {}).get("result", [])]
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

class EPMCMetadata(dataobj.DataObj):
    def __init__(self, raw):
        super(EPMCMetadata, self).__init__(raw)

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

    @property
    def journal(self):
        return self._get_single("journalInfo.journal.title", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def essn(self):
        return self._get_single("journalInfo.journal.essn", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def title(self):
        return self._get_single("title", self._utf8_unicode(), allow_coerce_failure=False)

class EPMCFullText(object):
    def __init__(self, raw):
        self.raw = raw
        try:
            self.xml = etree.fromstring(self.raw)
        except:
            raise EPMCFullTextException("Unable to parse XML", self.raw)

    @property
    def title(self):
        title_elements = self.xml.xpath("//title-group/article-title")
        if len(title_elements) > 0:
            return title_elements[0].text
        return None

    @property
    def is_aam(self):
        manuscripts = self.xml.xpath("//article-id[@pub-id-type='manuscript']")
        return len(manuscripts) > 0

    def get_licence_details(self):
        # get the licence type
        l = self.xml.xpath("//license")
        if len(l) > 0:
            l = l[0]
        else:
            return None, None, None
        type = l.get("license-type")
        url = l.get("{http://www.w3.org/1999/xlink}href")

        # get the paragraph(s) describing the licence
        para = self.xml.xpath("//license/license-p")
        out = ""
        for p in para:
            out += etree.tostring(p)

        return type, url, out

    @property
    def copyright_statement(self):
        cs = self.xml.xpath("//copyright-statement")
        if len(cs) > 0:
            return cs[0].text
        return None
