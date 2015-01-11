from flask import Blueprint, make_response, url_for, request, abort
import json
from octopus.lib.dataobj import ObjectSchemaValidationError
from octopus.core import app
from octopus.lib import plugin, webapp

blueprint = Blueprint('crud', __name__)

def _not_found():
    resp = make_response(json.dumps({"status" : "not found"}))
    resp.mimetype = "application/json"
    resp.status_code = 404
    return resp

def _bad_request(e):
    resp = make_response(json.dumps({"status" : "error", "error" : e.message}))
    resp.mimetype = "application/json"
    resp.status_code = 400
    return resp

def _created(obj, container_type):
    url = url_for("crud.entity", container_type=container_type, type_id=obj.id)
    resp = make_response(json.dumps({"status" : "success", "id" : obj.id, "location" : url }))
    resp.mimetype = "application/json"
    resp.headers["Location"] = url
    resp.status_code = 201
    return resp

def _success():
    resp = make_response(json.dumps({"status" : "success"}))
    return resp

def _get_class(container_type, operation):
    # get the CRUD configuration object
    cfgs = app.config.get("CRUD")
    if cfgs is None:
        return None

    # get the container configuration
    ct = cfgs.get(container_type)
    if ct is None:
        return None

    # get the model object reference
    m = ct.get("model")
    if m is None:
        return None

    # determine if the operation is permitted
    if operation not in ct:
        return None
    if not ct.get(operation).get("enable", False):
        return None

    return plugin.load_class(m)

@blueprint.route("/<container_type>", methods=["POST"])
@webapp.jsonp
def container(container_type=None):
    # if this is the creation of a new object
    if request.method == "POST":
        # load the data management class for this operation type
        klazz = _get_class(container_type, "create")
        if klazz is None:
            return _not_found()

        # get the data from the request
        data = json.loads(request.data)

        # make and save a new object
        try:
            obj = klazz(data)
        except ObjectSchemaValidationError as e:
            return _bad_request(e)

        # call save on the object
        obj.save()

        # return a useful response
        return _created(obj, container_type)

    abort(405)

@blueprint.route("/<container_type>/<type_id>", methods=["GET", "PUT", "DELETE"])
@webapp.jsonp
def entity(container_type=None, type_id=None):
    if request.method == "GET":
        # load the data management class for this operation type
        klazz = _get_class(container_type, "retrieve")
        if klazz is None:
            return _not_found()

        # get the existing object, json it, and return it
        obj = klazz.pull(type_id)
        if obj is None:
            return _not_found()

        resp = make_response(obj.json())
        resp.mimetype = "application/json"
        return resp

    elif request.method == "PUT":
        # load the data management class for this operation type
        klazz = _get_class(container_type, "update")
        if klazz is None:
            return _not_found()

        # get the existing record
        obj = klazz.pull(type_id)
        if obj is None:
            return _not_found()

        # ge the data to replace the object
        data = json.loads(request.data)
        try:
            obj.update(data)
        except ObjectSchemaValidationError as e:
            return _bad_request(e)

        # call save on the object
        obj.save()

        # return a useful response object
        return _success()

    elif request.method == "DELETE":
        # load the data management class for this operation type
        klazz = _get_class(container_type, "delete")
        if klazz is None:
            return _not_found()

        obj = klazz.pull(type_id)
        if obj is None:
            return _not_found()
        obj.delete()

        # return a useful response object
        return _success()

    abort(405)