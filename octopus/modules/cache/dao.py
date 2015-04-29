from octopus.modules.es import dao
from octopus.core import app

class CachedFileDAO(dao.ESDAO):
    __type__ = app.config.get("CACHE_ES_TYPE", "cache")
