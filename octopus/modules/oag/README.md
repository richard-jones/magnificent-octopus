# OAGR

## Monitor

To monitor the state of the OAGR job scheduler

Mount the ES query endpoint

    from octopus.modules.es.query import blueprint as query
    app.register_blueprint(query, url_prefix="/query")

Mount the OAGR monitor blueprint

    from octopus.modules.oag.monitor import blueprint as oagmonitor
    app.register_blueprint(oagmonitor, url_prefix='/oagr')

Specify a query configuration

    QUERY_ROUTE = {
        "query" : {
            "oagr" : {
                "auth" : False,
                "role" : None,
                "filters" : [],
                "dao" : "octopus.modules.oag.dao.JobsDAO"
            }
        }
    }

Specify the query endpoint in the javascript config

    CLIENT_JS_OAGR_QUERY_ENDPOINT = "/query/oagr"

