ELASTIC_SEARCH_HOST = "http://localhost:9200"
ELASTIC_SEARCH_INDEX = "db"

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