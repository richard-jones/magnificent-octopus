from octopus.modules.cache import dao
from octopus.lib import dataobj
from octopus.core import app
from datetime import datetime

import os

class CacheGenerator(object):
    def generate(self, path):
        raise NotImplementedError()

class CachedFile(dataobj.DataObj, dao.CachedFileDAO):
    """
    {
        "id" : "<name of the cache type>"
        "filename" : "<name of file on disk>",
        "last_updated" : "<when this cache file was last updated>",
        "timeout" : "<when this cache file times out>",
        "generating" : true|false
    }
    """

    @property
    def filename(self):
        return self._get_single("filename", coerce=self._utf8_unicode())

    @filename.setter
    def filename(self, val):
        self._set_single("filename", val, coerce=self._utf8_unicode())

    @property
    def timeout(self):
        return self._get_single("timeout", coerce=self._date_str())

    @timeout.setter
    def timeout(self, val):
        self._set_single("timeout", val, coerce=self._date_str())

    @property
    def generating(self):
        return self._get_single("generating", coerce=bool, default=False)

    @generating.setter
    def generating(self, val):
        self._set_single("generating", val, bool)

    @property
    def path(self):
        return os.path.join(app.config.get("CACHE_DIR"), self.id, self.filename)

    def is_stale(self):
        return datetime.utcnow() >= datetime.strptime(self.timeout, "%Y-%m-%dT%H:%M:%SZ")