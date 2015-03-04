from octopus.core import app
from octopus.lib import http
from octopus.lib import xml as xmlutil
import requests, codecs

class RomeoClientException(Exception):
    pass

class RomeoClient(object):
    def __init__(self, base_url=None, download_url=None, access_key=None):
        self.base_url = base_url if base_url is not None else app.config.get("ROMEO_API_BASE_URL")
        self.download_url = download_url if download_url is not None else app.config.get("ROMEO_DOWNLOAD_BASE_URL")
        self.access_key = access_key if access_key is not None else app.config.get("ROMEO_API_KEY")

    def download(self, output, format="csv"):
        url = self.download_url + "journal-title-issns/" + self.access_key + "/" + format + "/" # trailing slash is required
        resp = requests.get(url)
        with codecs.open(output, "wb", "utf8") as f:
            f.write(resp.text)

    def get_by_issn(self, issn):
        url = self.base_url + "?issn=" + http.quote(issn)
        app.logger.info("Looking up ISSN in Romeo with URL {x}".format(x=url))
        resp = http.get(url)
        if resp is None or resp.status_code != 200:
            app.logger.info("Unable to retrieve {x} from Romeo".format(x=issn))
            raise RomeoClientException("Unable to get by issn")
        xml = xmlutil.fromstring(resp.text)
        return SearchResult(xml)


class SearchResult(object):
    def __init__(self, xml):
        self.xml = xml

    @property
    def publishers(self):
        return [Publisher(el) for el in self.xml.xpath("//publisher")]

class Publisher(object):
    def __init__(self, xml):
        self.xml = xml

    def _archive_conditions(self, archiving_xpath, restrictions_xpath):
        pa = self.xml.xpath(archiving_xpath)
        pc = self.xml.xpath(restrictions_xpath)

        status = None
        if len(pa) > 0:
            status = pa[0].text
            if status is not None:
                status = status.strip()

        rest = []
        if len(pc) > 0:
            rest = [t.text.strip() for t in pc if t.text is not None]

        return status, rest

    def _parse_embargo(self, s):
        emb = xmlutil.fromstring("<emb>" + s + "</emb>")
        numel = emb.find("num")
        pel = emb.find("period")

        n = None
        if numel is not None and numel.text is not None:
            n = numel.text

        p = None
        if pel is not None:
            p = pel.get("units")

        return n, p

    def _embargo(self, restrictions):
        for rest in restrictions:
            if "embargo" in rest.lower():
                return self._parse_embargo(rest)
        return None, None

    @property
    def name(self):
        names = self.xml.xpath("//name")
        if len(names) > 0:
            return names[0].text

    @property
    def preprint(self):
        return self._archive_conditions("//prearchiving", "//prerestriction")

    @property
    def postprint(self):
        return self._archive_conditions("//postarchiving", "//postrestriction")

    @property
    def pdf(self):
        return self._archive_conditions("//pdfarchiving", "//pdfrestriction")

    @property
    def preprint_archiving(self):
        return self.preprint[0]

    @property
    def postprint_archiving(self):
        return self.postprint[0]

    @property
    def pdf_archiving(self):
        return self.pdf[0]

    @property
    def preprint_embargo(self):
        return self._embargo(self.preprint[1])

    @property
    def postprint_embargo(self):
        return self._embargo(self.postprint[1])

    @property
    def pdf_embargo(self):
        return self._embargo(self.pdf[1])