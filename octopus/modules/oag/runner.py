from octopus.modules.oag.oagr import JobRunner
from octopus.core import initialise, app
from octopus.lib import plugin, error_handler

import logging

if __name__ == "__main__":
    initialise()
    error_handler.setup_error_logging(app, "OAGR Runner Error", stdout_logging_level=logging.INFO)

    closure_path = app.config.get("OAGR_RUNNER_CALLBACK_CLOSURE")
    if closure_path is None:
        print "ERROR: cannot start job runner without OAGR_RUNNER_CALLBACK_CLOSURE defined"
        exit(0)

    fn = plugin.load_function(closure_path)
    if fn is None:
        print "ERROR: callback closure function not defined: " + closure_path + " - sert OAGR_RUNNER_CALLBACK_CLOSURE correctly"
        exit(0)

    print "Using closure " + closure_path + " to generate callback"

    cb = fn()
    if cb is None:
        print "ERROR: closure did not return anything.  Check your function at " + closure_path
        exit(0)

    print "Using " + str(cb) + " as OAGR callback"

    jr = JobRunner(callback=fn())
    jr.run()
