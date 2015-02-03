from octopus.core import app
import time, sys, traceback
from datetime import datetime
from octopus.modules.oag import client as oag
from octopus.modules.oag import dao

class JobRunner(object):
    def __init__(self, lookup_url=None, es_throttle=2, oag_throttle=5, verbose=True, callback=None):
        self.es_throttle = es_throttle
        # self.conn = esprit.raw.Connection(app.config.get("ELASTIC_SEARCH_HOST"), app.config.get("ELASTIC_SEARCH_DB"))
        # self.index = "jobs"
        self.lookup_url = lookup_url if lookup_url is not None else app.config.get("OAG_LOOKUP_URL")
        self.client = oag.OAGClient(lookup_url)
        self.verbose = verbose
        self.oag_throttle = oag_throttle
        self.callback = callback

    @classmethod
    def make_job(cls, state):
        r = JobRunner()
        return r.save_job(state)

    def has_due(self):
        return dao.JobsDAO.has_due()

    def job_statuses(self):
        return dao.JobsDAO.job_statuses()

    def save_job(self, state):
        print "Saving state to ElasticSearch ...",
        sys.stdout.flush()
        j = state.json()
        is_finished = state.finished()
        j["status"] = "finished" if is_finished else "active"
        obj = dao.JobsDAO(j)
        obj.save()
        print "Complete"
        return obj

    def cycle_state(self, state):
        if self.verbose:
            now = datetime.now()
            print now.strftime("%Y-%m-%d %H:%M:%S") + " Processing job " + state.id
            print state.print_parameters()
            print state.print_status_report()

        # issue the cycle request
        self.client.cycle(state, self.oag_throttle, self.verbose)
        if self.verbose:
            print state.print_status_report()

        # run the callback on the state
        if self.callback is not None:
            self.callback("cycle", state)

        # run the save method if there is one
        self.save_job(state)

        if state.finished():
            self.callback("finished", state)
            print "JOB " + state.id + " HAS COMPLETED!!!"
        else:
            # if we have done work here, update the next due time for the busy
            # loop aboge
            next = state.next_due()
            if next is not None:
                print "Next request is due at", datetime.strftime(next, "%Y-%m-%d %H:%M:%S"), "\n"

    def run(self):
        print "Starting OAGR ... Started"
        col_counter = 0
        while True:
            try:
                time.sleep(self.es_throttle)
                states = self.has_due()
                found = False
                for state, n, of in states:
                    found = True
                    col_counter = 0
                    print ""
                    print "Processing", n, "of", of, "in this round of jobs\n"
                    self.cycle_state(state)
                if not found:
                    print ".",
                    sys.stdout.flush()
                    col_counter += 1
                    if col_counter >= 36:
                        print ""
                        col_counter = 0
                else:
                    print "Finished job processing for this round"
            except Exception:
                app.logger.error(traceback.format_exc())
                msg = "Exception experienced in OAGR runner."
                if app.config.get("OAGR_EXIT_ON_EXCEPTION", False):
                    msg += " Exiting."
                    print msg
                    exit(0)
                else:
                    st = app.config.get("OAGR_EXCEPTION_SLEEP_TIME", 30)
                    msg += " Sleeping for {x}s before attempting to resume normal operation".format(x=st)
                    print msg
                    time.sleep(st)
