import csv

def csv_closure(success_file="oagr_success.csv", error_file="oagr_error.csv"):
    def csv_callback(state):
        successes = state.flush_success()
        errors = state.flush_error()
        with open(success_file, "a") as f:
            writer = csv.writer(f)
            for s in successes:
                identifier = s.get("identifier", [{}])[0].get("id")
                ltitle = s.get("license", [{}])[0].get("title")
                csv_row = [identifier, ltitle]
                clean_row = [unicode(c).encode("utf8", "replace") if c is not None else "" for c in csv_row]
                writer.writerow(clean_row)

        with open(error_file, "a") as f:
            writer = csv.writer(f)
            for e in errors:
                identifier = e.get("identifier", [{}]).get("id")
                msg = e.get("error")
                csv_row = [identifier, msg]
                clean_row = [unicode(c).encode("utf8", "replace") if c is not None else "" for c in csv_row]
                writer.writerow(clean_row)
    return csv_callback