import esprit
from esprit import mappings
from octopus.core import app
import json as jsonlib
from datetime import datetime
import dateutil.relativedelta as relativedelta

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

    def json(self):
        return jsonlib.dumps(self.data)

    def prep(self):
        pass

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