from flask import Blueprint, Response, request, url_for, make_response

from functools import wraps

from octopus.core import app
from octopus.lib.webapp import ssl_required

from sss.spec import Errors, HttpHeaders, ValidationException
from sss.core import Auth, SwordError, AuthException, DepositRequest, DeleteRequest

# create the global configuration and import the implementation classes
from sss.config import Configuration
config = Configuration(config_obj=app.config.get("SWORDV2_SERVER_CONFIG"))
Authenticator = config.get_authenticator_implementation()
SwordServer = config.get_server_implementation()

blueprint = Blueprint('swordv2_server', __name__)

HEADER_MAP = {
    HttpHeaders.in_progress : "in_progress",
    HttpHeaders.metadata_relevant : "metadata_relevant",
    HttpHeaders.on_behalf_of : "on_behalf_of"
}

STATUS_MAP = {
    400 : "400 Bad Request",
    401 : "401 Unauthorized",
    402 : "402 Payment Required",
    403 : "403 Forbidden",
    404 : "404 Not Found",
    405 : "405 Method Not Allowed",
    406 : "406 Not Acceptable",
    412 : "412 Precodition Failed",
    413 : "412 Request Entity Too Large",
    415 : "415 Unsupported Media Type"
}

def raise_error(sword_error, additional_headers=None):
    body = sword_error.error_document if not sword_error.empty else ""
    resp = make_response(body)
    resp.mimetype = "text/xml"
    resp.status_code = sword_error.status
    if additional_headers is not None:
        for k, v in additional_headers.iteritems():
            resp.headers[k] = v
    return resp

##################################################
## Authentication methods

def check_auth(username, password, obo=None):
    authenticator = Authenticator(config)
    auth = None
    try:
        auth = authenticator.basic_authenticate(username, password, obo)
    except AuthException as e:
        if e.authentication_failed:
            raise SwordError(status=401, empty=True)
        elif e.target_owner_unknown:
            raise SwordError(error_uri=Errors.target_owner_unknown, msg="unknown user " + str(obo) + " as on behalf of user")

    return auth

def basic_auth():
    auth = request.authorization
    if not auth:
        raise SwordError(status=401, empty=True)
    authobj = check_auth(auth.username, auth.password)
    if authobj is None:
        raise SwordError(status=401, empty=True)
    return authobj

###################################################
# Data extraction functions

def get_deposit(auth):
    d = DepositRequest()

    mapped_headers = request.headers

    h = HttpHeaders()
    d.set_from_headers(h.get_sword_headers(mapped_headers))

    if d.content_length > config.max_upload_size:
        raise SwordError(error_uri=Errors.max_upload_size_exceeded,
                        msg="Max upload size is " + str(config.max_upload_size) +
                        "; incoming content length was " + str(d.content_length))

    # get the body as a stream (which should be available as the mimetype
    # is not handled by default by Flask, we hope!)
    d.content_file = request.stream

    # set the filename
    d.filename = h.extract_filename(mapped_headers)

    # now just attach the authentication data and return
    d.auth = auth
    return d

###################################################
## Protocol operations

@blueprint.route('/service-document', methods=['GET'])
@ssl_required
def service_document():
    """
    GET the service document - returns an XML document
    - sub_path - the path provided for the sub-service document
    """
    try:
        auth = basic_auth()
    except SwordError as e:
        return raise_error(e, {'WWW-Authenticate': 'Basic realm="JPER"'})

    # if we get here authentication was successful and we carry on (we don't care who authenticated)
    ss = SwordServer(config, auth)
    sd = ss.service_document()

    resp = make_response(sd)
    resp.mimetype = "application/atomsvc+xml"
    return resp

@blueprint.route("/collection/<collection_id>", methods=["POST"])
@ssl_required
def collection(collection_id):
    """
    POST either an Atom Multipart request, or a simple package into the specified collection
    Args:
    - collection_id:   The ID of the collection as specified in the requested URL
    Returns a Deposit Receipt
    """

    try:
        # authenticate
        auth = basic_auth()

        # FIXME: this is not a full implementation yet, so probably we won't do this until later
        # check the validity of the request
        # self.validate_deposit_request(web, "6.3.3", "6.3.1", "6.3.2")

        # take the HTTP request and extract a Deposit object from it
        deposit = get_deposit(auth)

        # go ahead and process the deposit.  Anything other than a success
        # will be raised as a sword error
        ss = SwordServer(config, auth)
        result = ss.deposit_new(collection_id, deposit)

        # created
        content = ""
        if config.return_deposit_receipt:
            content = result.receipt

        resp = make_response(content)
        resp.mimetype = "application/atom+xml;type=entry"
        resp.headers["Location"] = result.location
        resp.status_code = 201

        return resp

    except SwordError as e:
        return raise_error(e)

@blueprint.route("/entry/<entry_id>", methods=["GET"])
@ssl_required
def entry(entry_id):
    pass

@blueprint.route("/entry/<entry_id>/content", methods=["GET"])
@ssl_required
def content(entry_id):
    pass

@blueprint.route("/entry/<entry_id>/statement/<type>", methods=["GET"])
@ssl_required
def statement(entry_id):
    pass
