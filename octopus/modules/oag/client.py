from datetime import datetime, timedelta
import json, requests, time, sys, uuid
from copy import deepcopy
from octopus.core import app
from octopus.lib import http

class RequestState(object):
    _timestamp_format = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, identifiers, timeout=None, back_off_factor=None, max_back_off=None, max_retries=None, batch_size=None, start=None):
        self.id = uuid.uuid4().hex

        self.success = {}
        self.error = {}
        self.pending = {}
        self.maxed = {}

        self.success_buffer = []
        self.error_buffer = []

        self.start = datetime.utcnow() if start is None else start

        if timeout is None:
            timeout = app.config.get("OAG_STATE_DEFAULT_TIMEOUT")
        self.timeout = self.start + timedelta(seconds=timeout) if timeout is not None else None

        if back_off_factor is None:
            back_off_factor = app.config.get("OAG_STATE_BACK_OFF_FACTOR", 1)
        self.back_off_factor = back_off_factor

        if max_back_off is None:
            max_back_off = app.config.get("OAG_STATE_MAX_BACK_OFF", 120)
        self.max_back_off = max_back_off

        if max_retries is None:
            max_retries = app.config.get("OAG_STATE_MAX_RETRIES", None)
        self.max_retries = max_retries

        if batch_size is None:
            batch_size = app.config.get("OAG_STATE_BATCH_SIZE", 1000)
        self.batch_size = batch_size

        for ident in identifiers:
            self.pending[ident] = {"init" : self.start, "due" : self.start, "requested" : 0}

    def print_parameters(self):
        params = "Timeout: " + str(self.timeout) + "\n"
        params += "Back Off Factor: " + str(self.back_off_factor) + "\n"
        params += "Max Back Off: " + str(self.max_back_off) + "\n"
        params += "Max Tries per Identifier: " + str(self.max_retries) + "\n"
        params += "Batch Size: " + str(self.batch_size)
        return params

    def print_status_report(self):
        status = str(len(self.success.keys())) + " received; " + \
                 str(len(self.error.keys())) + " errors; " + \
                 str(len(self.pending.keys())) + " pending; " + \
                 str(len(self.maxed.keys())) + " maxed"
        return status

    def finished(self):
        if len(self.pending.keys()) == 0:
            return True
        if self.timeout is not None:
            if datetime.utcnow() > self.timeout:
                return True
        return False

    def get_due(self):
        now = datetime.utcnow()
        return [p for p in self.pending.keys() if self.pending[p].get("due") < now]

    def next_due(self):
        earliest = None
        for p, o in self.pending.iteritems():
            if earliest is None or o.get("due") < earliest:
                earliest = o.get("due")
        return earliest

    def _record_maxed(self, id):
        self.maxed[id] = self.pending[id]
        del self.pending[id]
        if "due" in self.maxed[id]:
            del self.maxed[id]["due"]

    def record_requested(self, identifiers):
        for id in identifiers:
            if id in self.pending:
                self.pending[id]["requested"] += 1
                if self.max_retries is not None and self.pending[id]["requested"] >= self.max_retries:
                    self._record_maxed(id)
            else:
                print "ERROR: id {id} is not in the pending list".format(id=id)


    def record_result(self, result):
        now = datetime.utcnow()

        successes = result.get("results", [])
        errors = result.get("errors", [])
        processing = result.get("processing", [])

        for s in successes:
            id = s.get("identifier")[0].get("id")
            ourrecord = self.pending.get(id)
            if ourrecord is None:
                print "No record of pending id " + id
                continue
            self.success[id] = deepcopy(ourrecord)
            self.success[id]["requested"] += 1
            self.success[id]["found"] = now
            del self.success[id]["due"]
            del self.pending[id]
        self.success_buffer.extend(successes)

        for e in errors:
            id = e.get("identifier").get("id")
            ourrecord = self.pending.get(id)
            if ourrecord is None:
                print "No record of pending id " + id
                continue
            self.error[id] = deepcopy(ourrecord)
            self.error[id]["requested"] += 1
            self.error[id]["found"] = now
            del self.error[id]["due"]
            del self.pending[id]
        self.error_buffer.extend(errors)

        for p in processing:
            id = p.get("identifier").get("id")
            ourrecord = self.pending.get(id)
            if ourrecord is None:
                print "ERROR: No record of pending id " + id
                continue
            self.pending[id]["requested"] += 1
            self.pending[id]["due"] = self._backoff(self.pending[id]["requested"])
            if self.max_retries is not None and self.pending[id]["requested"] >= self.max_retries:
                self._record_maxed(id)

    def flush_success(self):
        buffer = self.success_buffer
        self.success_buffer = []
        return buffer

    def flush_error(self):
        buffer = self.error_buffer
        self.error_buffer = []
        return buffer

    @classmethod
    def from_json(cls, j):
        state = RequestState([])

        state.id = j.get("id")
        if j.get("timetout"):
            state.timeout = datetime.strptime(j.get("timeout"), cls._timestamp_format)
        state.start = datetime.strptime(j.get("start"), cls._timestamp_format)
        state.back_off_factor = j.get("back_off_factor")
        state.max_back_off = j.get("max_back_off")
        state.batch_size = j.get("batch_size")
        if j.get("max_retries"):
            state.max_retries = j.get("max_retries")

        for s in j.get("success", []):
            obj = deepcopy(s)
            obj["init"] = datetime.strptime(obj["init"], cls._timestamp_format)
            obj["found"] = datetime.strptime(obj["found"], cls._timestamp_format)
            state.success[s.get("id")] = obj

        for s in j.get("error", []):
            obj = deepcopy(s)
            obj["init"] = datetime.strptime(obj["init"], cls._timestamp_format)
            obj["found"] = datetime.strptime(obj["found"], cls._timestamp_format)
            state.error[s.get("id")] = obj

        for s in j.get("pending", []):
            obj = deepcopy(s)
            obj["init"] = datetime.strptime(obj["init"], cls._timestamp_format)
            obj["due"] = datetime.strptime(obj["due"], cls._timestamp_format)
            state.pending[s.get("id")] = obj

        for s in j.get("maxed", []):
            obj = deepcopy(s)
            obj["init"] = datetime.strptime(obj["init"], cls._timestamp_format)
            state.maxed[s.get("id")] = obj

        return state

    def json(self):
        data = {}

        data["id"] = self.id
        data["start"] = datetime.strftime(self.start, self._timestamp_format)
        if self.timeout is not None:
            data["timeout"] = datetime.strftime(self.start, self._timestamp_format)
        data["back_off_factor"] = self.back_off_factor
        data["max_back_off"] = self.max_back_off
        if self.max_retries is not None:
            data["max_retries"] = self.max_retries
        data["batch_size"] = self.batch_size

        data["success"] = []
        for k in self.success:
            obj = {"id" : k}
            obj.update(self.success[k])
            obj["init"] = datetime.strftime(obj["init"], self._timestamp_format)
            obj["found"] = datetime.strftime(obj["found"], self._timestamp_format)
            data["success"].append(obj)

        data["error"] = []
        for k in self.error:
            obj = {"id" : k}
            obj.update(self.error[k])
            obj["init"] = datetime.strftime(obj["init"], self._timestamp_format)
            obj["found"] = datetime.strftime(obj["found"], self._timestamp_format)
            data["error"].append(obj)

        data["pending"] = []
        for k in self.pending:
            obj = {"id" : k}
            obj.update(self.pending[k])
            obj["init"] = datetime.strftime(obj["init"], self._timestamp_format)
            obj["due"] = datetime.strftime(obj["due"], self._timestamp_format)
            data["pending"].append(obj)

        data["maxed"] = []
        for k in self.maxed:
            obj = {"id" : k}
            obj.update(self.maxed[k])
            obj["init"] = datetime.strftime(obj["init"], self._timestamp_format)
            data["maxed"].append(obj)

        return data

    def _backoff(self, times):
        now = datetime.utcnow()
        seconds = 2**times * self.back_off_factor
        seconds = seconds if seconds < self.max_back_off else self.max_back_off
        return now + timedelta(seconds=seconds)


class OAGClient(object):
    def __init__(self, lookup_url=None):
        self.lookup_url = lookup_url if lookup_url is not None else app.config.get("OAG_LOOKUP_URL")

    def cycle(self, state, throttle=0, verbose=False):
        due = state.get_due()
        batches = self._batch(due, state.batch_size)
        if verbose:
            print str(len(due)) + " due; requesting in " + str(len(batches)) + " batches"
        first = True
        i = 1
        print "Processing batch ",
        for batch in batches:
            if first:
                first = False
            elif throttle > 0:
                time.sleep(throttle)

            # first try and get the result - this could result in an HTTP error, and we
            # don't want that to kill the thread.  If it fails, record a request against the
            # identifier but leave it pending
            result = None
            recorded = False
            try:
                result = self._query(batch)
            except requests.exceptions.HTTPError as e:
                # record the records in this batch as requested once more
                state.record_requested(batch)
                recorded = True

            # if we get a result, then record it.  Otherwise, again record the batch as requested
            # but leave it in pending.
            if result is not None:
                state.record_result(result)
            else:
                # record the records in this batch as requested once more
                if not recorded:
                    state.record_requested(batch)

            print i,
            sys.stdout.flush()
            i += 1
        print ""
        return state

    def _batch(self, ids, batch_size=1000):
        batches = []
        start = 0
        while True:
            batch = ids[start:start + batch_size]
            if len(batch) == 0: break
            batches.append(batch)
            start += batch_size
        return batches

    def _query(self, batch, retries=10):
        data = json.dumps(batch)
        resp = http.post(self.lookup_url, retries=retries, headers={'Accept':'application/json'}, data=data)

        if resp is None:
            return None
        elif resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            resp.raise_for_status()

def oag_it(lookup_url, identifiers,
           timeout=None, back_off_factor=1, max_back_off=120, max_retries=None, batch_size=1000,
            verbose=True, throttle=5,
            callback=None, save_state=None):
    state = RequestState(identifiers, timeout=timeout, back_off_factor=back_off_factor, max_back_off=max_back_off, max_retries=max_retries, batch_size=batch_size)
    client = OAGClient(lookup_url)

    if verbose:
        print "Making requests to " + lookup_url + " for " + str(len(identifiers)) + " identifiers"
        print state.print_parameters()
        print state.print_status_report()

    next = state.next_due()
    while True:
        # check whether we're supposed to do anything yet
        now = datetime.utcnow()
        if now < next:
            continue

        # if a cycle is due, issue it
        client.cycle(state, throttle, verbose)
        if verbose:
            print state.print_status_report()

        # run the callback on the state
        if callback is not None:
            callback("cycle", state)

        # run the save method if there is one
        if save_state is not None:
            save_state(state)

        # if we are finished, break
        if state.finished():
            callback("finished", state)
            print "FINISHED"
            break

        # if we have done work here, update the next due time for the busy
        # loop aboge
        next = state.next_due()
        print "Next request is due at", datetime.strftime(next, "%Y-%m-%d %H:%M:%S")
