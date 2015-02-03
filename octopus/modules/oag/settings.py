# OAG Client configuration
########################################

OAG_LOOKUP_URL = "http://howopenisit.org/lookup"

# amount of time before a request state in its entirity times out
OAG_STATE_DEFAULT_TIMEOUT = None

# multiplier on incremental back off.  The back-off algorithm doubles the wait time each request, multiplied
# by this factor, so adjust it to speed or slow the back-off
OAG_STATE_BACK_OFF_FACTOR = 1

# maximim number of seconds to wait between requests for identifiers, irrespective of the back-off rules
OAG_STATE_MAX_BACK_OFF = 120

# maximum number of times to retry an identifier
OAG_STATE_MAX_RETRIES = None

# batch size to send to OAG in
OAG_STATE_BATCH_SIZE = 100

# OAGR Job runner configuration
#######################################

OAGR_JOBS_ES_TYPE = "oagr_jobs"

OAGR_RUNNER_CALLBACK_CLOSURE = "octopus.modules.oag.callbacks.csv_closure"

# if the runner experiences an exception, should it exit, or carry on
OAGR_EXIT_ON_EXCEPTION = False

# if the runner experiences an exception, and does not exit, how long should it wait for before attempting to
# resume normal operation
OAGR_EXCEPTION_SLEEP_TIME = 30



# OAGR Monitor UI
#######################################

CLIENTJS_OAGR_QUERY_ENDPOINT = "/query/oagr"

"""
example query route which you should enable in your main service configuration

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
"""
