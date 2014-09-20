ELASTIC_SEARCH_HOST = "http://localhost:9200"
ELASTIC_SEARCH_INDEX = "db"

INITIALISE_INDEX = True

from esprit import mappings
ELASTIC_SEARCH_MAPPINGS = {
    "example" : mappings.for_type(
        "example",
            mappings.properties(mappings.type_mapping("location", "geo_point")),
            mappings.dynamic_templates(
            [
                mappings.EXACT,
            ]
        )
    )
}

QUERY_ROUTE = {
    "query" : {
        "index" : {
            "auth" : False,
            "role" : None,
            "filters" : ["default"],
            "dao" : "portality.dao.MyDAO"
        }
    }
}

def default_filter(query):
    pass

QUERY_FILTERS = {
    "default" : default_filter
}