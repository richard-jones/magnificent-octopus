from octopus.core import app
from octopus.lib import webapp, plugin, dates
from octopus.modules.account.factory import AccountFactory

from flask import Blueprint, request, abort, make_response

import esprit, json, re


blueprint = Blueprint('searchapi', __name__)

###############################################
## Authentication/Authorisation

class AuthenticationException(Exception):
    pass

class AuthorisationException(Exception):
    pass

def _auth(roles):
    api_key = request.values.get("api_key")
    if api_key is None:
        raise AuthenticationException("No API key provided for route which requires authentication")

    klazz = AccountFactory.get_model()
    try:
        acc = klazz.get_by_api_key(api_key)
    except AttributeError:
        msg = "You have authenticated API routes, but your Account model does not support get_by_api_key"
        app.logger.error(msg)
        raise Exception(msg)

    if len(roles) == 0:
        return acc

    for r in roles:
        if not acc.has_role(r):
            raise AuthorisationException("Your account does not have permission for that action")

    return acc

###################################################

###################################################
## Input sanitisation

class BadRequest(Exception):
    pass

def _sanitise(cfg, q, page, psize, sort_by, sort_dir):
    # check the page is an integer greater than 0
    try:
        page = int(page)
    except:
        raise BadRequest("Page number is not an integer")
    if page < 1:
        page = 1

    # limit the page size as per the configuration
    try:
        psize = int(psize)
    except:
        raise BadRequest("Page size is not an integer")
    if psize > cfg.get("max_page_size", 100):
        psize = cfg.get("max_page_size", 100)
    elif psize < 1:
        psize = cfg.get("default_page_size", 10)

    if sort_dir is not None:
        sort_dir = sort_dir.lower()
        if sort_dir not in ["asc", "desc"]:
            raise BadRequest("sortDir must be one of 'asc' or 'desc'")

    # with the easy stuff done, let's make sure the query is legit, and make our
    # required modifications to it

    if not _allowed(q):
        raise BadRequest("Query contains disallowed Lucene features")

    # check that we have been given a query
    if q is None or q == "":
        raise BadRequest("Search query must be specified")

    search_no_mod = cfg.get("search_no_mod", [])
    search_subs = cfg.get("search_subs", {})
    search_prefix = cfg.get("search_prefix")
    q = _query_substitute(q, search_subs, search_prefix, search_no_mod)
    q = _escape(q)

    sort_subs = cfg.get("sort_subs")
    sort_prefix = cfg.get("sort_prefix")
    if sort_by is not None:
        sort_by = _prep_sort(sort_by, sort_subs, sort_prefix)

    # calculate the position of the from cursor in the document set
    fro = (page - 1) * psize

    return q, fro, page, psize, sort_by, sort_dir

def _prep_sort(sort_by, sort_subs, prefix=None):
    if sort_by is None:
        return None

    if sort_by in sort_subs:
        sort_by = sort_subs[sort_by]
        return sort_by

    if prefix is not None:
        sort_by = prefix + sort_by

    return sort_by

def _query_substitute(query, substitutions, prefix=None, no_mod=None):
    if len(substitutions.keys()) == 0 and prefix is None:
        return query

    # apply the regex escapes to the substitutions, so we know they
    # are ready to be matched
    # This escapes any instance of ":" in the incoming field (to be substituted), as : is also the
    # separator for fields/values
    escsubs = {}
    for k, v in substitutions.iteritems():
        escsubs[k.replace(":", "\\:")] = v

    # define a function which takes the match group and returns the
    # substitution if there is one
    def rep(match):
        ret = match.group(1)
        if ret in no_mod:
            return ret

        # first apply the substitutions
        for k, v in escsubs.iteritems():
            if k == ret:
                return v

        # if no substitution is applied, apply the prefix to the match
        if not ret.startswith(prefix):
            ret = prefix + ret

        return ret

    # define the regular expressions for splitting and then extracting
    # the field to be substituted
    split_rx = "([^\\\\]:)"     # matches any unescaped :, plus the character before it
    field_rx = "([^\s\+\-\(\)\"]+?):$"

    # split the query around any unescaped colons.  This will group the unescaped colons with the character before it,
    # because of the capture group
    bits = re.split(split_rx, query)

    # because of that, stitch back together the split sections and the separators.  At the end, each value apart from
    # the last one will end with a ":" (such that whatever is before the colon is the field (plus some extra stuff before that)
    segs = [bits[i] + bits[i+1] for i in range(0, len(bits), 2) if i+1 < len(bits)] + [bits[len(bits) - 1]] if len(bits) % 2 == 1 else []

    # substitute the fields as required
    subs = []
    for seg in segs:
        if seg.endswith(":"):
            subs.append(re.sub(field_rx, rep, seg))
        else:
            subs.append(seg)

    return ":".join(subs)

def _allowed(query, wildcards=False, fuzzy=False):
    if not wildcards:
        rx = "(.+[^\\\\][\?\*]+.*)"
        if re.search(rx, query):
            return False

    if not fuzzy:
        # this covers both fuzzy searching and proximity searching
        rx = "(.+[^\\\\]~[0-9]{0,1}[\.]{0,1}[0-9]{0,1})"
        if re.search(rx, query):
            return False

    return True

def _escape(query):
    # just escapes all instances of "/" in the query with "\\/"

    # Function which does the replacement
    def slasher(m):
        return m.group(0)[0] + "\\/"


    # the regular expression which looks for an unescaped /
    slash_rx = "[^\\\\]/"

    # because the regex matches two characters, neighbouring /s will not both
    # get replaced at the same time because re.sub looks at "non overlapping matches".
    # This means "//" will not be properly escaped.  So, we run the re.subn
    # function repeatedly until the number of replacements drops to 0
    count = 1
    while count > 0:
        query, count = re.subn(slash_rx, slasher, query)

    return query

########################################################

# simple proxy for an underlying ES index, queried using a query string
@blueprint.route('/<cfg_name>', methods=['GET'])
@webapp.jsonp
def search(cfg_name):
    cfg = app.config.get("SEARCHAPI", {}).get(cfg_name)
    if cfg is None:
        abort(404)

    qb = cfg.get("query_builder")
    if qb is None:
        abort(404)

    dao_path = cfg.get("dao")
    if dao_path is None:
        abort(404)

    acc = None
    if cfg.get("auth", False):
        try:
            acc = _auth(cfg.get("roles", []))
        except AuthenticationException:
            abort(401)
        except AuthorisationException:
            abort(403)

    # get the values for the 3 key bits of search info: the query, the page number and the page size
    q = request.values.get("q")
    page = request.values.get("page", 1)
    psize = request.values.get("pageSize", cfg.get("default_page_size", 10))
    sort_by = request.values.get("sortBy")
    sort_dir = request.values.get("sortDir")

    # send the passed-in values for sanitisation, and get the actual parameters that
    # we are going to search on
    try:
        q, fro, page, psize, sort_by, sort_dir = _sanitise(cfg, q, page, psize, sort_by, sort_dir)
    except BadRequest:
        abort(400)

    # assemble the query
    query_builder = plugin.load_class(qb)
    query = query_builder(q, fro, psize, sort_by, sort_dir, acc)

    # load the DAO class and send the query through it
    klazz = plugin.load_class(dao_path)
    res = klazz.query(q=query.query())

    # check to see if there was a search error
    if res.get("error") is not None:
        abort(400)

    # unpack the results and pull out the search metadata
    obs = esprit.raw.unpack_json_result(res)
    total = res.get("hits", {}).get("total", 0)

    # optionally filter the result objects as per the config
    filter = cfg.get("results_filter")
    if filter is not None:
        fn = plugin.load_function(filter)
        obs = [fn(o) for o in obs]

    # build the response object
    response = {
        "total" : total,
        "page" : page,
        "pageSize" : psize,
        "timestamp" : dates.now(),
        "query" : q,
        "results" : obs
    }

    resp = make_response(json.dumps(response))
    resp.mimetype = "application/json"
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp