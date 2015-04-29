import os

# To use the cache, you'll need to add this to your ES mappings config
#ELASTIC_SEARCH_MAPPINGS = [
#   "octopus.modules.cache.dao.CachedFileDAO"
#]

# list of classes which can generate cache files
CACHE_GENERATORS = {
#   "name_of_cachable" : {
#       "class" : "path.to.class",
#       "timeout" : 1800        # in seconds
#    }
}

# The default cache directory is to a file in the root of the app, but you should absolutely
# override this
CACHE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "..", "cache")

# index type to use for the cache
CACHE_ES_TYPE = "cache"