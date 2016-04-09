from octopus.core import app
from octopus.lib import plugin

import schedule
import time

def configure():
    """
    Build scheduler tasks, which are equivalent to asking schedule these kinds of things:

    schedule.every(10).minutes.do(job)
    schedule.every().hour.do(job)
    schedule.every().day.at("10:30").do(job)
    schedule.every().monday.do(job)
    schedule.every().wednesday.at("13:15").do(job)
    """
    for cfg in app.config.get("SCHEDULER_TASKS", []):
        # unpack the config tuple
        interval, unit, at, do = cfg

        # make sure that the config is viable
        if interval is not None:
            interval = int(interval)
        assert isinstance(unit, basestring), "Unit must be provided, and be a string"
        if at is not None:
            assert isinstance(at, basestring), "At, if provided, must be a string"
        fn = plugin.load_function(do)
        assert fn is not None, u"{x} does not resolve to a function".format(x=do)

        # first setup an interval
        cascade = None
        if interval is not None:
            cascade = schedule.every(interval)
        else:
            cascade = schedule.every()

        # set the unit
        cascade = object.__getattribute__(cascade, unit)

        # specify the time period
        if at is not None:
            cascade = cascade.at(at)

        cascade.do(fn)

def run():
    configure()
    while True:
        schedule.run_pending()
        time.sleep(1)

def cheep():
    print "**Cheep**"