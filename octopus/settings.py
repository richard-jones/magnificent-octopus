import os
from esprit import mappings

# ========================
# MAIN SETTINGS

# base path, to the directory where this settings file lives
BASE_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

# contact info
ADMIN_NAME = "WNA"
ADMIN_EMAIL = "sysadmin@cottagelabs.com"
ADMINS = ["richard@cottagelabs.com"]
SUPPRESS_ERROR_EMAILS = False  # should be set to False in production and True in staging

# service info
SERVICE_NAME = "JiscMonitor"
SERVICE_TAGLINE = ""
HOST = "0.0.0.0"
DEBUG = True
PORT = 5013
SSL = False

# elasticsearch settings
ELASTIC_SEARCH_HOST = "http://localhost:9200" # remember the http:// or https://
ELASTIC_SEARCH_DB = "monitor"
INITIALISE_INDEX = False # whether or not to try creating the index and required index types on startup

QUERY_ENDPOINT = "http://staging.doaj.cottagelabs.com/query/journal,article"

# can anonymous users get raw JSON records via the query endpoint?
PUBLIC_ACCESSIBLE_JSON = True

# =======================
# email settings

SMTP_SERVER = None

SMTP_PORT = None

# override these in your app.cfg, and don't put them in version control
SMTP_USER = None
SMTP_PASS = None


# ========================
# MAPPING SETTINGS

# a dict of the ES mappings. identify by name, and include name as first object name
# and identifier for how non-analyzed fields for faceting are differentiated in the mappings
"""
FACET_FIELD = ".exact"
MAPPINGS = {
    "reactor" : mappings.for_type(
        "reactor",
            mappings.properties(mappings.type_mapping("location", "geo_point")),
            mappings.dynamic_templates(
            [
                mappings.EXACT,
            ]
        )
    )
}
"""

# ========================
# QUERY SETTINGS

# list index types that should not be queryable via the query endpoint
NO_QUERY = []
SU_ONLY = ["account"]

# list additional terms to impose on anonymous users of query endpoint
# for each index type that you wish to have some
# must be a list of objects that can be appended to an ES query.bool.must
# for example [{'term':{'visible':True}},{'term':{'accessible':True}}]
ANONYMOUS_SEARCH_TERMS = {
    # "pages": [{'term':{'visible':True}},{'term':{'accessible':True}}]
}

# a default sort to apply to query endpoint searches
# for each index type that you wish to have one
# for example {'created_date' + FACET_FIELD : {"order":"desc"}}
DEFAULT_SORT = {
    # "pages": {'created_date' + FACET_FIELD : {"order":"desc"}}
}

QUERY_ROUTE = {
    "user_query" : {"default_filter": True},
#    "admin_query" : {"role" : "admin", "default_filter": False},
#    "publisher_query" : {"role" : "publisher", "default_filter" : False, "owner_filter" : True}
}

# ==========================
# MAP INTEGRATION

# add this in app.cfg
GOOGLE_MAP_API_KEY = None