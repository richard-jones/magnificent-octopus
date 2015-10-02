import esprit
from esprit import mappings
from octopus.core import app
import json as jsonlib
from datetime import datetime
import dateutil.relativedelta as relativedelta
import os, threading
from octopus.lib import plugin
from octopus.modules.es.initialise import put_mappings, put_example

class ESDAO(esprit.dao.DomainObject):
    __type__ = 'index'
    __conn__ = esprit.raw.Connection(app.config.get('ELASTIC_SEARCH_HOST'), app.config.get('ELASTIC_SEARCH_INDEX'))
    __es_version__ = app.config.get("ELASTIC_SEARCH_VERSION")

    #####################################################
    ## overrides on Domain Object

    @classmethod
    def delete_by_query(cls, query, conn=None, es_version="0.90.13", type=None):
        esv = cls.__es_version__
        if esv is None:
            esv = es_version
        super(ESDAO, cls).delete_by_query(query, conn=conn, es_version=esv, type=type)

    def save(self, **kwargs):
        self.prep()
        super(ESDAO, self).save(**kwargs)

    ######################################################
    ## Octopus specific functions

    @classmethod
    def mappings(cls):
        return {
            cls.__type__ : mappings.for_type(
                cls.__type__,
                    mappings.properties(mappings.type_mapping("location", "geo_point")),
                    mappings.dynamic_templates(
                    [
                        mappings.EXACT,
                    ]
                )
            )
        }

    @classmethod
    def example(cls):
        return cls()

    @classmethod
    def self_init(cls, *args, **kwargs):
        pass

    def json(self):
        return jsonlib.dumps(self.data)

    def prep(self):
        pass

class RollingTypeESDAO(ESDAO):
    # should the dynamic type be checked for existance, and initialised
    # with a mapping or an example document
    __init_dynamic_type__ = False

    # if initialising the dynamic type, should it use mappings()
    __init_by_mapping__ = False

    # if initialising the dynamic type, should it use example()
    __init_by_example__ = False

    # the order in which the DAO should look for an index type to query
    __read_preference__ = ["next", "curr", "prev"]

    # create a lock for this DAO to use so that the modifications to the files can
    # be synchronised
    _lock = threading.RLock()

    @classmethod
    def _mint_next_type(cls):
        return cls.__type__ + datetime.utcnow().strftime("%Y%m%d%H%M%S")

    @classmethod
    def _roll_dir(cls):
        return os.path.join(app.config.get("ESDAO_ROLLING_DIR"), cls.__type__)

    @classmethod
    def _get_cfg(cls, pos):
        return app.config.get("ESDAO_ROLLING_{x}_{y}".format(x=pos.upper(), y=cls.__type__.upper()))

    @classmethod
    def _set_cfg(cls, pos, val):
        app.config["ESDAO_ROLLING_{x}_{y}".format(x=pos.upper(), y=cls.__type__.upper())] = val

    @classmethod
    def publish(cls, conn=None):
        # synchronise access
        with cls._lock:
            if conn is None:
                conn = cls.__conn__

            dir = cls._roll_dir()
            prev = os.path.join(dir, "prev")
            curr = os.path.join(dir, "curr")
            next = os.path.join(dir, "next")

            # we only want to continue if next exists
            if not os.path.exists(next):
                return

            previous = None
            current = None
            n = None

            # read all the types directly out of the files
            if os.path.exists(prev) and os.path.isfile(prev):
                with open(prev) as o:
                    previous = o.read()

            if os.path.exists(curr) and os.path.isfile(curr):
                with open(curr) as o:
                    current = o.read()

            if os.path.exists(next) and os.path.isfile(next):
                with open(next) as o:
                    n = o.read()

            # write current back to previous
            if current is not None:
                with open(prev, "wb") as o:
                    o.write(current)

            # write next to current
            if next is not None:
                with open(curr, "wb") as o:
                    o.write(n)

            # get rid of the next file
            if os.path.exists(next) and os.path.isfile(next):
                os.remove(next)

            # set the app configuration
            cls._set_cfg("prev", current)
            cls._set_cfg("curr", n)
            cls._set_cfg("next", None)

            # delete the old previous index type
            if previous is not None:
                esprit.raw.delete(conn, previous)

    @classmethod
    def rollback(cls, conn=None):
         # synchronise access
        with cls._lock:
            if conn is None:
                conn = cls.__conn__

            dir = cls._roll_dir()
            prev = os.path.join(dir, "prev")
            curr = os.path.join(dir, "curr")
            next = os.path.join(dir, "next")

            # we only want to continue if prev exists
            if not os.path.exists(prev):
                return

            previous = None
            current = None
            n = None

            # read all the types directly out of the files
            if os.path.exists(prev) and os.path.isfile(prev):
                with open(prev) as o:
                    previous = o.read()

            if os.path.exists(curr) and os.path.isfile(curr):
                with open(curr) as o:
                    current = o.read()

            if os.path.exists(next) and os.path.isfile(next):
                with open(next) as o:
                    n = o.read()

            # write current to next
            if current is not None:
                with open(next, "wb") as o:
                    o.write(current)

            # write previous to current
            if previous is not None:
                with open(curr, "wb") as o:
                    o.write(previous)

            # get rid of the previous file
            if os.path.exists(prev) and os.path.isfile(prev):
                os.remove(prev)

            # set the app configuration
            cls._set_cfg("prev", None)
            cls._set_cfg("curr", previous)
            cls._set_cfg("next", current)

            # delete the old next index type
            if next is not None:
                esprit.raw.delete(conn, next)

    @classmethod
    def drop_next(cls, conn=None):
        with cls._lock:
            if conn is None:
                conn = cls.__conn__

            dir = cls._roll_dir()
            next = os.path.join(dir, "next")
            if not os.path.exists(next):
                return
            with open(next) as o:
                n = o.read()
            os.remove(next)
            cls._set_cfg("next", None)
            esprit.raw.delete(conn, n)

    @classmethod
    def self_init(cls, *args, **kwargs):
        tname = kwargs.get("type_name")
        if tname is None:
            tname = cls._mint_next_type()

        write = kwargs.get("write", True)
        write_to = kwargs.get("write_to", "curr")

        dir = cls._roll_dir()
        f = os.path.join(dir, write_to)

        # since file reading/writing is going on, we need to synchronise access to this bit
        with cls._lock:
            # we only want to write on initialise if we have not already initialised this
            # index type.  So, if the file exists (e.g. "curr"), then no need to init
            if write:
                if os.path.exists(f):
                    return

            # if we get to here either the write_to needs to be initialised, or we haven't
            # been asked to "write" the index type we're initialising

            # there are two ways this might be initialised - by mapping or by example
            # 1. by mapping
            if cls.__init_by_mapping__:
                mps = cls.mappings()
                put_mappings({tname : {tname : mps[cls.__type__][cls.__type__]}})
            # 2. by example
            elif cls.__init_by_example__:
                ex = cls.example()
                put_example(tname, ex)

            # finally, write the type name to the file
            if write:
                if not os.path.exists(dir):
                    os.mkdir(dir)
                with open(f, "wb") as o:
                    o.write(tname)


    @classmethod
    def dynamic_read_types(cls):
        dir = cls._roll_dir()
        for pref in cls.__read_preference__:
            # first look to see if it is set in the config
            t = cls._get_cfg(pref)
            # t = app.config.get("ESDAO_ROLLING_" + pref.upper())
            if t is not None:
                return t

            # if not next check to see if there's a file
            f = os.path.join(dir, pref)
            if os.path.exists(f) and os.path.isfile(f):
                with open(f) as o:
                    t = o.read()
                    cls._set_cfg(pref, t)
                    # app.config["ESDAO_ROLLING_" + pref.upper()] = t
                    return t

        # if we don't get anything, return the base type
        return cls.__type__


    @classmethod
    def dynamic_write_type(cls):
        # look to see if the next index is already set, in which case we
        # can return
        next = cls._get_cfg("next")
        # next = app.config.get("ESDAO_ROLLING_NEXT")
        if next is not None:
            return next

        # since there could be several threads trying to do the same thing, lock
        # this thread until the file/index has been sorted out
        with cls._lock:
            # if not, read it from the directory
            dir = cls._roll_dir()
            f = os.path.join(dir, "next")
            if os.path.exists(f) and os.path.isfile(f):
                with open(f) as o:
                    next = o.read()
                cls._set_cfg("next", next)
                # app.config["ESDAO_ROLLING_NEXT"] = next
                return next

            # if it wasn't in the directory we need to make it
            tname = cls._mint_next_type()
            if cls.__init_dynamic_type__:
                # find out if this class needs to self-init
                for cname in app.config.get("ELASTIC_SEARCH_SELF_INIT", []):
                    klazz = plugin.load_class(cname)
                    if issubclass(cls, klazz):
                        cls.self_init(type_name=tname, write=False)

            # now write the file
            if not os.path.exists(dir):
                os.mkdir(dir)
            with open(f, "wb") as o:
                o.write(tname)

            return tname

class TimeBoxedTypeESDAO(ESDAO):

    # FIXME: this is just a placeholder, we're not doing a proper impl of this yet
    # should the dynamic type be checked for existance, and initialised
    # with a mapping or an example document
    __init_dynamic_type__ = False

    FORMAT_MAP = {
        "year" : "%Y",
        "month" : "%Y%m",
        "day" : "%Y%m%d",
        "hour" : "%Y%m%d%H",
        "minute" : "%Y%m%d%H%M",
        "second" : "%Y%m%d%H%M%S"
    }

    #####################################################
    ## overrides on Domain Object

    @classmethod
    def dynamic_read_types(cls):
        gran = cls._get_time_granularity()
        ts = cls._boundary_timestamp(gran)
        lookback = cls._get_lookback()
        tss = cls._lookback_timestamps(lookback, gran, ts)
        return [cls._format_type(gran, ts) for ts in tss]

    @classmethod
    def dynamic_write_type(cls):
        # first generate the type name
        gran = cls._get_time_granularity()
        ts = cls._boundary_timestamp(gran)
        wt = cls._format_type(gran, ts)

        # if might be that the type does not yet exist, in which case we
        # may need to create it
        if cls.__init_dynamic_type__:
            # FIXME: we don't have the use case for this yet, so it's just a placeholder
            # ultimately we'll probably want to factor the type initialisation stuff out of
            # octopus.modules.es.initialise so that we can re-use it here
            pass

        return wt

    ######################################################
    ## Private methods for handling time boxing

    @classmethod
    def _get_time_granularity(cls):
        cfarg = "ESDAO_TIME_BOX_" + cls.__type__.upper()
        period = app.config.get(cfarg)
        if period is None:
            period = app.config.get("ESDAO_DEFAULT_TIME_BOX", "month")
        return period

    @classmethod
    def _get_lookback(cls):
        cfarg = "ESDAO_TIME_BOX_LOOKBACK_" + cls.__type__.upper()
        lookback = app.config.get(cfarg)
        if lookback is None:
            lookback = app.config.get("ESDAO_DEFAULT_TIME_BOX_LOOKBACK", 0)
        return lookback

    @classmethod
    def _boundary_timestamp(cls, granularity):
        now = datetime.utcnow()

        # this gives us our most coarse-grained date period
        # [current year, 1, 1, 0, 0 ,0] = (say) 2015-01-01 00:00:00
        args = [now.year] + [1, 1, 0, 0, 0]
        if granularity == "year":
            return datetime(*args)

        # granularity of month or greater
        args[1] = now.month
        if granularity == "month":
            return datetime(*args)

        # granularity of day or greater
        args[2] = now.day
        if granularity == "day":
            return datetime(*args)

        # granularity of hour or greater
        args[3] = now.hour
        if granularity == "hour":
            return datetime(*args)

        # granularity of minute or greater
        args[4] = now.minute
        if granularity == "minute":
            return datetime(*args)

        # granularity of second
        args[5] = now.second
        return datetime(*args)

    @classmethod
    def _lookback_timestamps(cls, lookback, granularity, latest_timestamp):
        rds = []
        if granularity == "year":
            rds = [relativedelta.relativedelta(years=x) for x in range(1, lookback + 1)]
        if granularity == "month":
            rds = [relativedelta.relativedelta(months=x) for x in range(1, lookback + 1)]
        if granularity == "day":
            rds = [relativedelta.relativedelta(days=x) for x in range(1, lookback + 1)]
        if granularity == "hour":
            rds = [relativedelta.relativedelta(hours=x) for x in range(1, lookback + 1)]
        if granularity == "minute":
            rds = [relativedelta.relativedelta(minutes=x) for x in range(1, lookback + 1)]
        if granularity == "second":
            rds = [relativedelta.relativedelta(seconds=x) for x in range(1, lookback + 1)]

        tss = [latest_timestamp]
        for rd in rds:
            tss.append(latest_timestamp - rd)

        return tss

    @classmethod
    def _format_type(cls, granularity, timestamp):
        fmt = cls.FORMAT_MAP.get(granularity)
        return cls.__type__ + timestamp.strftime(fmt)



class QueryStringQuery(object):
    def __init__(self, qs, fro, psize):
        self.qs = qs
        self.fro = fro
        self.psize = psize

    def query(self):
        return {
            "query" :{
                "query_string" : {
                    "query" : self.qs
                }
            },
            "from" : self.fro,
            "size" : self.psize
        }