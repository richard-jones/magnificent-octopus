from octopus.core import app
from octopus.lib import http

import json

class Lantern(object):
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url if base_url is not None else app.config.get("LANTERN_BASE_URL", "https://api.cottagelabs.com/service/lantern")
        self.api_key = api_key if api_key is not None else app.config.get("LANTERN_API_KEY")

    def check(self):
        url = self._get_url()
        resp = http.get(url)
        if resp.status_code == 200:
            return True
        return False

    def create_job(self, email, filename, ident_objects):
        """
        create a job with the specified parameters.

        ident_objects are of the form

        [{
            "Article title" : "<title of the article>",
            "DOI" : "<article DOI>",
            "PMCID" : "<Europe PMC identifier for the article (starting with 'PMC')>",
            "PMID" : "<PubMed identifier for the article>"
        }]

        You must provide at least one of these fields per ident_object

        :param email: email to receive the completed job notification
        :param filename: the name to give to the data you upload
        :param ident_objects: list of identifier objects
        :return:
        """
        request = {"email" : email, "filename" : filename, "list" : ident_objects}
        url = self._get_url()
        resp = http.post(url, data=json.dumps(request), headers={"Content-Type": "application/json; charset=UTF-8"})
        if resp is not None:
            return resp.json()
        return None


    def get_job_info(self, job_id):
        url = self._get_url(job_id)
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None

    def get_original_data(self, job_id):
        url = self._get_url(job_id + "/original")
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.content
        return None

    def get_progress(self, job_id):
        url = self._get_url(job_id + "/progress")
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None

    def get_todo(self, job_id):
        url = self._get_url(job_id + "/todo")
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None

    def get_results(self, job_id):
        url = self._get_url(job_id + "/results")
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None

    def get_results_csv(self, job_id):
        url = self._get_url(job_id + "/results", {"format" : "csv"})
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.content
        return None

    def list_jobs(self, email):
        url = self._get_url("jobs/" + http.quote(email))
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None

    def get_quota(self, email):
        url = self._get_url("quota/" + http.quote(email))
        resp = http.get(url)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None


    def _get_url(self, endpoint=None, params=None):
        url = self.base_url
        if endpoint is not None:
            url += "/" + endpoint
        if params is None:
            params = {}
        if self.api_key is not None:
            params["apikey"] = self.api_key
        if len(params.keys()) > 0:
            args = [k + "=" + v for k, v in params.iteritems()]
            qs = "&".join(args)
            url += "?" + qs
        return url

