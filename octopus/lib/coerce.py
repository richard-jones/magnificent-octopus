import locale, urlparse, string, re
import numbers
from octopus.lib import dates, locality

class CoerceFactory(object):

    @classmethod
    def get(cls, coerce_type):
        # first, some easy name to function mappings
        if coerce_type == "unicode":
            return to_unicode
        elif coerce_type == "integer":
            return to_int
        elif coerce_type == "float":
            return to_float
        elif coerce_type == "url":
            return to_url
        elif coerce_type == "bool":
            return to_bool

        # now some pre-defined calls to closures
        elif coerce_type == "utcdatetime":
            return cls.closure("datestr")
        elif coerce_type == "isolang_2letter":
            return cls.closure("isolang", output_format="alpha2")
        elif coerce_type == "bigenddate":
            return cls.closure("datestr", out_format="%Y-%m-%d")

    @classmethod
    def closure(cls, coerce_type, **kwargs):
        if coerce_type == "datestr":
            return date_str(**kwargs)
        elif coerce_type == "isolang":
            return to_isolang(**kwargs)
        elif coerce_type == "datestamp":
            return to_datestamp(**kwargs)

#########################################################
## Data coerce functions

def to_unicode(val):
    if isinstance(val, unicode):
        return val
    elif isinstance(val, basestring):
        try:
            return val.decode("utf8", "strict")
        except UnicodeDecodeError:
            raise ValueError(u"Could not decode string")
    else:
        return unicode(val)

def to_int(val):
    # strip any characters that are outside the ascii range - they won't make up the int anyway
    # and this will get rid of things like strange currency marks
    if isinstance(val, unicode):
        val = val.encode("ascii", errors="ignore")

    # try the straight cast
    try:
        return int(val)
    except ValueError:
        pass

    # could have commas in it, so try stripping them
    try:
        return int(val.replace(",", ""))
    except ValueError:
        pass

    # try the locale-specific approach
    try:
        return locale.atoi(val)
    except ValueError:
        pass

    raise ValueError(u"Could not convert string to int: {x}".format(x=val))


def to_float(val):
    if val == "":
        return None

    # strip any characters that are outside the ascii range - they won't make up the float anyway
    # and this will get rid of things like strange currency marks
    if isinstance(val, unicode):
        val = val.encode("ascii", errors="ignore")

    # try the straight cast
    try:
        return float(val)
    except ValueError:
        pass

    # now we're going to have to try some stuff that takes into account possible locales
    thousands = [",", " ", ".", "'"]
    decimals = [".", ",", "'"]
    punc = list(set(thousands + decimals))

    clean = ""
    for c in val:
        if c in punc or c in string.digits:
            clean += c
    if clean == "":
        return None

    val = clean


    # try the straight cast again
    try:
        return float(val)
    except ValueError:
        pass

    # try the most obvious locale - this probably means this function doesn't work
    # so well for other locales
    try:
        return float(val.replace(",", ""))
    except ValueError:
        pass

    # try the locale-specific approach
    try:
        return locale.atof(val)
    except ValueError:
        pass

    # ok, now try the various combinations of locale-related layouts
    #dot_dec_rx = ".+(?<=\.)\d+"
    #comma_dec_rx = ".+(?<=,)\d+"
    #quote_dec_rx = ".+(?<=')\d+"

    #comma_th_rx = ".+,{1}\d{3}[\d',\.]*"
    #space_th_rx = ".+ {1}\d{3}[\d',\.]*"
    #dot_th_rx = ".+\.{1}\d{3}[\d',\.]*"
    #quote_th_rx = ".+'{1}\d{3}[\d',\.]*"

    raise ValueError(u"Could not convert string to float: '{x}'".format(x=val))

def to_url(val):
    if val is None:
        return None

    # parse with urlparse
    url = urlparse.urlparse(val)

    # now check the url has the minimum properties that we require
    if url.scheme and url.scheme.startswith("http"):
        return to_unicode(val)
    else:
        raise ValueError(u"Could not convert string {val} to viable URL".format(val=val))

def to_bool(val):
    """Conservative boolean cast - don't cast lists and objects to True, just existing booleans, numbers and strings."""
    if val is None:
        return None
    if val is True or val is False:
        return val

    if isinstance(val, basestring):
        if val.lower() in ['true', "yes", "t", "1"]:
            return True
        elif val.lower() in ['false', "no", "f", "0"]:
            return False
        raise ValueError(u"Could not convert string {val} to boolean. Expecting string to either say 'true' or 'false' (not case-sensitive).".format(val=val))
    
    elif isinstance(val, numbers.Number):
        return bool(val)

    raise ValueError(u"Could not convert {val} to boolean. Expect either boolean or string.".format(val=val))

def to_currency_code(val):
    l = locality.Locality()
    cc = l.currency_code_for(val)
    if cc is None:
        raise ValueError(u"Could not map {x} to a known currency code".format(x=val))
    return cc

##############################################################
## Data coerce closures

def date_str(in_format=None, out_format=None):
    def datify(val):
        return dates.reformat(val, in_format=in_format, out_format=out_format)

    return datify

def to_datestamp(in_format=None):
    def stampify(val):
        return dates.parse(val, format=in_format)

    return stampify

def to_isolang(output_format=None):
    """
    :param output_format: format from input source to putput.  Must be one of:
        * alpha3
        * alt3
        * alpha2
        * name
        * fr
    Can be a list in order of preference, too
    :return:
    """
    # delayed import, since we may not always want to load the whole dataset for a dataobj
    from octopus.lib import isolang as dataset

    # sort out the output format list
    if output_format is None:
        output_format = ["alpha3"]
    if not isinstance(output_format, list):
        output_format = [output_format]

    def isolang(val):
        if val is None:
            return None
        l = dataset.find(val)
        for f in output_format:
            v = l.get(f)
            if v is None or v == "":
                continue
            return v

    return isolang

