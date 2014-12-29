from octopus.modules.oag.oagr import JobRunner
from octopus.modules.oag import callbacks
from octopus.core import initialise

if __name__ == "__main__":
    initialise()
    jr = JobRunner(callback=callbacks.csv_closure("oagr_success.csv", "oagr_error.csv"))
    jr.run()