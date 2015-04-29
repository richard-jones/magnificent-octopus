from octopus.core import app
from octopus.modules.cache import models
from octopus.lib import plugin
import os
from datetime import datetime, timedelta
from operator import itemgetter
from multiprocessing import Process

class CacheException(Exception):
    pass

def load_file(name):
    cf = models.CachedFile.pull(name)

    # if there is not file to serve, or the file is stale, trigger the regen
    if cf is None or cf.is_stale():
        trigger_regen(name)

    # whether we triggered the regen or not, return the current result.  Next caller will
    # get the regenerated file
    return cf

def trigger_regen(name):
    p = Process(target=generate_file, args=(name,))
    p.start()

def generate_file(name, respect_timeout=False):
    # check that we have a generator for this cache type
    generator = app.config.get("CACHE_GENERATORS", {}).get(name, {}).get("class")
    if generator is None:
        raise CacheException("No generator configured for {x}".format(x=name))

    # figure out the timeout on this file
    timeout = app.config.get("CACHE_GENERATORS", {}).get(name, {}).get("timeout")
    if timeout is None:
        raise CacheException("No timeout specified for {x}".format(x=name))

    # get the file record to which this pertains (or make one if it is new)
    cf = models.CachedFile.pull(name)
    if cf is None:
        cf = models.CachedFile()
        cf.id = name
    else:
        # if the file is currently generating (perhaps in another thread), just return
        if cf.generating:
            return

        # if the file is not stale, and we are respecting the timeout, just return
        if not cf.is_stale() and respect_timeout:
            return

        # switch the generating flag to true and re-save
        cf.generating = True
        cf.save()           # Note that we don't do a blocking save, because we want to update this record again asap, and this data is throwaway

    # create a suitable filename
    filename = "{x}_{y}".format(x=name, y=datetime.utcnow().strftime("%Y-%m-%d_%H%M"))

    # get the cache directory sorted out
    dir = os.path.join(app.config.get("CACHE_DIR"), name)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # finally get the file path ready
    filepath = os.path.join(dir, filename)

    # now instantiate the class and ask it to generate the file
    klazz = plugin.load_class(generator)
    inst = klazz()
    inst.generate(filepath)

    # now calculate the timeout
    to = datetime.utcnow() + timedelta(seconds=timeout)

    # now update the cached file record
    cf.filename = filename
    cf.generating = False
    cf.timeout = to.strftime("%Y-%m-%dT%H:%M:%SZ")
    cf.save()

    # finally, clean up the cache directory of any old files
    cleanup_cache_dir(dir)

    return cf

def cleanup_cache_dir(dir):
    # remove all but the two latest files
    files = [(c, os.path.getmtime(os.path.join(dir, c)) ) for c in os.listdir(dir)]
    sorted_files = sorted(files, key=itemgetter(1), reverse=True)

    if len(sorted_files) > 2:
        for c, lm in sorted_files[2:]:
            os.remove(os.path.join(dir, c))
