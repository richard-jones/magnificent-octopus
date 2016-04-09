from flask import Blueprint, make_response, url_for, request, abort
import json
from octopus.lib.dataobj import ObjectSchemaValidationError, DataSchemaException, DataStructureException
from octopus.core import app
from octopus.lib import webapp
from octopus.modules.crud.factory import CRUDFactory
from octopus.modules.account.factory import AccountFactory
from octopus.modules.crud import models

blueprint = Blueprint('crud', __name__)

################################################
## Pre-packaged response codes and bodies

def _not_found():
    app.logger.debug("Sending 404 Not Found")
    resp = make_response(json.dumps({"status" : "not found"}))
    resp.mimetype = "application/json"
    resp.status_code = 404
    return resp

def _bad_request(e):
    app.logger.info("Sending 400 Bad Request from client: {x}".format(x=e.message))
    resp = make_response(json.dumps({"status" : "error", "error" : e.message}))
    resp.mimetype = "application/json"
    resp.status_code = 400
    return resp

def _created(obj, container_type, include_location=True):
    app.logger.info("Sending 201 Created: {x} {y}".format(x=container_type, y=obj.id))
    body = obj.created_response()
    if include_location:
        if body is None:
            body = {}
        if "location" not in body:
            location = url_for("crud.entity", container_type=container_type, type_id=obj.id)
            body["location"] = location
    resp = make_response(json.dumps(body))
    resp.mimetype = "application/json"
    if include_location:
        resp.headers["Location"] = body["location"]
    resp.status_code = 201
    return resp

def _updated(obj, container_type, include_location=True):
    app.logger.info("Sending 200 OK for update: {x} {y}".format(x=container_type, y=obj.id))
    body = obj.updated_response()
    if include_location:
        if body is None:
            body = {}
        if "location" not in body:
            location = url_for("crud.entity", container_type=container_type, type_id=obj.id)
            body["location"] = location
    resp = make_response(json.dumps(body))
    resp.mimetype = "application/json"
    if include_location:
        resp.headers["Location"] = body["location"]
    resp.status_code = 200
    return resp

def _deleted(obj, container_type):
    app.logger.info("Sending 200 OK for delete: {x} {y}".format(x=container_type, y=obj.id))
    body = obj.deleted_response()
    resp = make_response(json.dumps(body))
    resp.mimetype = "application/json"
    resp.status_code = 200
    return resp

def _success():
    app.logger.debug("Sending 200 OK")
    resp = make_response(json.dumps({"status" : "success"}))
    resp.mimetype = "application/json"
    resp.status_code = 200
    return resp

def _unauthorised(error):
    app.logger.info("Sending 401 Unauthorised from client: {x}".format(x=error))
    resp = make_response(json.dumps({"status" : "unauthorised", "error" : error}))
    resp.mimetype = "application/json"
    resp.status_code = 401
    return resp

def _forbidden(error):
    app.logger.info("Sending 403 Forbidden from client: {x}".format(x=error))
    resp = make_response(json.dumps({"status" : "forbidden", "error" : error}))
    resp.mimetype = "application/json"
    resp.status_code = 403
    return resp

###############################################
## Authentication/Authorisation

def _auth(container_type, method):
    cfg = app.config.get("CRUD", {}).get(container_type, {}).get(method, {})
    if not cfg.get("auth", False):
        return None

    api_key = request.values.get("api_key")
    if api_key is None:
        raise models.AuthenticationException("No API key provided for route which requires authentication")

    klazz = AccountFactory.get_model()
    try:
        acc = klazz.get_by_api_key(api_key)
    except AttributeError:
        msg = "You have authenticated API routes, but your Account model does not support get_by_api_key"
        app.logger.error(msg)
        raise Exception(msg)

    roles = cfg.get("roles", [])
    if len(roles) == 0:
        return acc

    for r in roles:
        if not acc.has_role(r):
            raise models.AuthorisationException("Your account does not have permission for that action")

    return acc

################################################
## Web routes

@blueprint.route("/<container_type>", methods=["POST"])
@webapp.jsonp
def container(container_type=None):
    # if this is the creation of a new object
    if request.method == "POST":
        app.logger.info("Request for creation of new object of type {x}".format(x=container_type))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "create")
        if klazz is None:
            return _not_found()

        # determine if authNZ is required, and carry it out
        try:
            acc = _auth(container_type, "create")
        except models.AuthenticationException as e:
            return _unauthorised(e.message)
        except models.AuthorisationException as e:
            return _forbidden(e.message)

        # get the data from the request
        data = json.loads(request.data)

        # make and save a new object
        try:
            obj = klazz(data, request.headers, acc)
        except ObjectSchemaValidationError as e:
            app.logger.info("Error processing create request {x}".format(x=e.message))
            return _bad_request(e)
        except DataSchemaException as e:
            app.logger.info("Error processing create request {x}".format(x=e.message))
            return _bad_request(e)
        except DataStructureException as e:
            app.logger.info("Error processing create request {x}".format(x=e.message))
            return _bad_request(e)

        # call save on the object
        obj.save()

        # return a useful response
        include_location = app.config.get("CRUD", {}).get(container_type, {}).get("create", {}).get("response", {}).get("location", True)
        return _created(obj, container_type, include_location)

    abort(405)

@blueprint.route("/<container_type>/<path:type_id>", methods=["GET", "PUT", "DELETE"])
@webapp.jsonp
def entity(container_type=None, type_id=None):
    if request.method == "GET":
        app.logger.info("Retrieve request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "retrieve")
        if klazz is None:
            return _not_found()

        # determine if authNZ is required, and carry it out
        try:
            acc = _auth(container_type, "retrieve")
        except models.AuthenticationException as e:
            return _unauthorised(e.message)
        except models.AuthorisationException as e:
            return _forbidden(e.message)

        # get the existing object, json it, and return it
        obj = klazz.pull(type_id, acc)
        if obj is None:
            return _not_found()

        resp = make_response(obj.json())
        resp.mimetype = "application/json"
        return resp

    elif request.method == "PUT":
        app.logger.info("Update request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "update")
        if klazz is None:
            return _not_found()

        # determine if authNZ is required, and carry it out
        try:
            acc = _auth(container_type, "update")
        except models.AuthenticationException as e:
            return _unauthorised(e.message)
        except models.AuthorisationException as e:
            return _forbidden(e.message)

        # get the existing record
        obj = klazz.pull(type_id, acc)
        if obj is None:
            return _not_found()

        # ge the data to replace the object
        data = json.loads(request.data)
        try:
            obj.update(data)
        except ObjectSchemaValidationError as e:
            app.logger.info("Error processing update request {x}".format(x=e.message))
            return _bad_request(e)
        except DataSchemaException as e:
            app.logger.info("Error processing update request {x}".format(x=e.message))
            return _bad_request(e)
        except DataStructureException as e:
            app.logger.info("Error processing update request {x}".format(x=e.message))
            return _bad_request(e)

        # call save on the object
        obj.save()

        # return a useful response object
        include_location = app.config.get("CRUD", {}).get(container_type, {}).get("update", {}).get("response", {}).get("location", True)
        return _updated(obj, container_type, include_location)

    elif request.method == "POST":
        app.logger.info("Append request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "append")
        if klazz is None:
            return _not_found()

        # determine if authNZ is required, and carry it out
        try:
            acc = _auth(container_type, "append")
        except models.AuthenticationException as e:
            return _unauthorised(e.message)
        except models.AuthorisationException as e:
            return _forbidden(e.message)

        # get the existing record
        obj = klazz.pull(type_id, acc)
        if obj is None:
            return _not_found()

        # ge the data to replace the object
        data = json.loads(request.data)
        try:
            obj.append(data)
        except ObjectSchemaValidationError as e:
            app.logger.info("Error processing append request {x}".format(x=e.message))
            return _bad_request(e)
        except DataSchemaException as e:
            app.logger.info("Error processing append request {x}".format(x=e.message))
            return _bad_request(e)
        except DataStructureException as e:
            app.logger.info("Error processing append request {x}".format(x=e.message))
            return _bad_request(e)

        # call save on the object
        obj.save()

        # return a useful response object
        include_location = app.config.get("CRUD", {}).get(container_type, {}).get("update", {}).get("response", {}).get("location", True)
        return _updated(obj, container_type, include_location)

    elif request.method == "DELETE":
        app.logger.info("Delete request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "delete")
        if klazz is None:
            return _not_found()

        # determine if authNZ is required, and carry it out
        try:
            acc = _auth(container_type, "delete")
        except models.AuthenticationException as e:
            return _unauthorised(e.message)
        except models.AuthorisationException as e:
            return _forbidden(e.message)

        obj = klazz.pull(type_id, acc)
        if obj is None:
            return _not_found()

        try:
            obj.delete()
        except models.AuthorisationException as e:
            return _forbidden(e.message)

        # return a useful response object
        return _deleted(obj, container_type)

    abort(405)