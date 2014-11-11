from octopus.core import app
import requests, codecs

class RomeoClient(object):
    def __init__(self, base_url=None, download_url=None, access_key=None):
        self.base_url = base_url if base_url is not None else app.config.get("ROMEO_API_BASE_URL")
        self.download_url = base_url if base_url is not None else app.config.get("ROMEO_DOWNLOAD_BASE_URL")
        self.access_key = access_key if access_key is not None else app.config.get("ROMEO_API_KEY")

    def download(self, output, format="csv"):
        url = self.download_url + "journal-title-issns/" + self.access_key + "/" + format + "/" # trailing slash is required
        resp = requests.get(url)
        with codecs.open(output, "wb", "utf8") as f:
            f.write(resp.text)

