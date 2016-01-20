from octopus.core import app
from datetime import datetime, timedelta
from random import randint

def parse(s, format=None, guess=True):
    s = s.strip()

    if format is not None:
        try:
            return datetime.strptime(s, format)
        except ValueError as e:
            if not guess:
                raise e

    for f in app.config.get("DATE_FORMATS", []):
        try:
            return datetime.strptime(s, f)
        except ValueError as e:
            pass

    raise ValueError("Unable to parse {x} with any known format".format(x=s))

def format(d, format=None):
    if format is None:
        format = app.config.get("DEFAULT_DATE_FORMAT")
    return unicode(d.strftime(format))

def reformat(s, in_format=None, out_format=None):
    return format(parse(s, format=in_format), format=out_format)

def now():
    return format(datetime.utcnow())

def before_now(seconds):
    return datetime.utcnow() - timedelta(seconds=seconds)

def day_ranges(fro, to):
    aday = timedelta(days=1)

    # first, workout when the next midnight point is
    next_day = fro + aday
    next_midnight = datetime(next_day.year, next_day.month, next_day.day)

    # in the degenerate case, to is before the next midnight, in which case they both
    # fall within the one day range
    if next_midnight > to:
        return [(format(fro), format(to))]

    # start the range off with the remainder of the first day
    ranges = [(format(fro), format(next_midnight))]

    # go through each day, adding to the range, until the next day is after
    # the "to" date, then finish up and return
    current = next_midnight
    while True:
        next = current + aday
        if next > to:
            ranges.append((format(current), format(to)))
            break
        else:
            ranges.append((format(current), format(next)))
            current = next

    return ranges

def random_date(fro=None, to=None):
    if fro is None:
        fro = parse("1970-01-01T00:00:00Z")
    if to is None:
        to = datetime.utcnow()

    span = int((to - fro).total_seconds())
    s = randint(0, span)
    return format(to - timedelta(seconds=s))