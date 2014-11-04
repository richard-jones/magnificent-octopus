##############################################################
# Basic ElasticSearch connectivity settings
##############################################################

ELASTIC_SEARCH_HOST = "http://localhost:9200"
ELASTIC_SEARCH_INDEX = "db"

##############################################################
# Index setup and mappings
##############################################################

INITIALISE_INDEX = True

# an array of DAO classes from which to retrieve the ES mappings to be
# loaded into the index during initialisation
ELASTIC_SEARCH_MAPPINGS = [
    # service.dao.MyDAO
]

##############################################################
# Query Endpoint Configuration
##############################################################

QUERY_ROUTE = {
    "query" : {                                 # the URL route at which it is mounted
        "index" : {                             # the URL name for the index type being queried
            "auth" : False,                     # whether the route requires authentication
            "role" : None,                      # if authenticated, what role is required to access the query endpoint
            "filters" : ["default"],            # names of the standard filters to apply to the query
            "dao" : "octopus.dao.MyDAO"       # classpath for DAO which accesses the underlying ES index
        }
    }
}

def default_filter(query):
    pass

QUERY_FILTERS = {
    "default" : default_filter
}

##############################################################
# Compound Field Auto-Complete Configuration
##############################################################

AUTOCOMPLETE_COMPOUND = {
    "name" : {                                  # name of the autocomplete, as represented in the URL (have as many of these sections as you need)
        "fields" : ["name", "description"],     # fields to return in the compound result
        "field_name_map" : {                    # map field name to name it will be referred to in the result
            "name" : "my_name",
            "description" : "my_description"
        },
        "filters" : {                           # filters to apply to the result set
            "name.exact" : {                    # field on which to filter
                "start_wildcard" : True,        # apply start wildcard?
                "end_wildcard": True,           # apply end wildcard?
                "boost" : 2.0                   # boost to apply to matches on this field
            },
            "description.exact" : {
                "start_wildcard" : True,
                "end_wildcard": True,
                "boost" : 1.0
            }
        },
        "default_size" : 10,                    # if no size param is specified, this is how big to make the response
        "max_size" : 25,                        # if a size param is specified, this is the limit above which it won't go
        "dao" : "octopus.dao.MyDAO"           # classpath for DAO which accesses the underlying ES index
    }
}

# configuration option to pass through to the javascript UI
CLIENTJS_ES_COMPOUND_ENDPOINT = "/autocomplete/compound"