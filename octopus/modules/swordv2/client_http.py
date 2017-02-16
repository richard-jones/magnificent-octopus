from sword2 import HttpLayer, HttpResponse
from octopus.lib import http
import json
from requests.auth import HTTPBasicAuth

class OctopusHttpResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        self.resp = args[0]
        self.code = kwargs["status"] if "status" in kwargs else None

    def __getitem__(self, att):
        return self.get(att)

    def __repr__(self):
        return self.resp.__repr__()

    @property
    def status(self):
        if self.code is not None:
            return self.code
        return self.resp.status_code

    def get(self, att, default=None):
        if att == "status":
            if self.code is not None:
                return self.code
            return self.resp.status_code
        if self.resp is not None:
            return self.resp.headers.get(att, default)
        else:
            return default

    def keys(self):
        if self.resp is not None:
            return self.resp.headers.keys()
        else:
            return []

class OctopusHttpLayer(HttpLayer):
    def __init__(self, *args, **kwargs):
        self.username = None
        self.password = None
        self.auth = None
        self._args = args
        self._kwargs = kwargs

    def add_credentials(self, username, password):
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)

    def request(self, uri, method, headers=None, payload=None):    # Note that body can be file-like
        resp = None
        if method == "GET":
            resp = http.get(uri, headers=headers, auth=self.auth, **self._kwargs)
        elif method == "POST":
            resp = http.post(uri, headers=headers, data=payload, auth=self.auth, **self._kwargs)
        elif method == "PUT":
            resp = http.put(uri, headers=headers, data=payload, auth=self.auth, **self._kwargs)
        elif method == "DELETE":
            resp = http.delete(uri, headers=headers, auth=self.auth, **self._kwargs)

        if resp is None:
            return OctopusHttpResponse(None, status=408), None

        return OctopusHttpResponse(resp), resp.text

