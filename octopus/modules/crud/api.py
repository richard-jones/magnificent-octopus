from flask import Blueprint, make_response, url_for, request, abort
import json
from octopus.lib.dataobj import ObjectSchemaValidationError
from octopus.core import app
from octopus.lib import webapp
from octopus.modules.crud.factory import CRUDFactory

blueprint = Blueprint('crud', __name__)

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

def _created(obj, container_type):
    app.logger.info("Sending 201 Created: {x} {y}".format(x=container_type, y=obj.id))
    url = url_for("crud.entity", container_type=container_type, type_id=obj.id)
    resp = make_response(json.dumps({"status" : "success", "id" : obj.id, "location" : url }))
    resp.mimetype = "application/json"
    resp.headers["Location"] = url
    resp.status_code = 201
    return resp

def _success():
    app.logger.debug("Sending 200 OK")
    resp = make_response(json.dumps({"status" : "success"}))
    return resp

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

        # get the data from the request
        data = json.loads(request.data)

        # make and save a new object
        try:
            obj = klazz(data, request.headers)
        except ObjectSchemaValidationError as e:
            app.logger.info("Error processing create request {x}".format(x=e.message))
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
        app.logger.info("Retrieve request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "retrieve")
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
        app.logger.info("Update request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "update")
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
            app.logger.info("Error processing update request {x}".format(x=e.message))
            return _bad_request(e)

        # call save on the object
        obj.save()

        # return a useful response object
        return _success()

    elif request.method == "DELETE":
        app.logger.info("Delete request for {x} {y}".format(x=container_type, y=type_id))

        # load the data management class for this operation type
        klazz = CRUDFactory.get_class(container_type, "delete")
        if klazz is None:
            return _not_found()

        obj = klazz.pull(type_id)
        if obj is None:
            return _not_found()
        obj.delete()

        # return a useful response object
        return _success()

    abort(405)