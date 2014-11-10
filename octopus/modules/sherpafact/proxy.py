from octopus.core import app

from flask import Blueprint, request, abort, make_response
import re, json

from octopus.lib import webapp
from octopus.modules.sherpafact.client import FactClient

blueprint = Blueprint('fact', __name__)

@blueprint.route('/')
@webapp.jsonp
def factapi():
    # we will be given a journal/issn string, and a list of funder ids
    try:
        journal_or_issn = request.values.get("journal_or_issn").strip()
        funders = request.values.get("funders").strip()
    except:
        abort(400)

    # determine if the string we have been given is an issn
    is_issn = _is_issn(journal_or_issn)

    # turn the comma delimited list of funders into an actual list
    funders = [f.strip() for f in funders.split(",")]

    # create the client, and then issue the relevant query, depending on whether we've been given an issn or not
    client = FactClient()
    if is_issn:
        # if it's an ISSN, that's nice and easy
        facts = client.query(funders, issn=journal_or_issn, trail=True)
    else:
        # if a journal, we do the fuzziest match possible
        facts = client.query(funders, journal_title=journal_or_issn, query_type=FactClient.QUERY_CONTAINS, trail=True)

    resp = make_response(json.dumps(facts.raw))
    resp.mimetype = "application/json"
    return resp



ISSN_REGEX = re.compile(r'^\d{4}-\d{3}(\d|X|x){1}$')

def _is_issn(candidate):
    matches = re.match(ISSN_REGEX, candidate)
    return matches is not None