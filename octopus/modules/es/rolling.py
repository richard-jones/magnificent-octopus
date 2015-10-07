from flask import Blueprint, request
from octopus.core import app
from octopus.lib import webapp, plugin

blueprint = Blueprint('rolling', __name__)

@blueprint.route('/publish', methods=['POST'])
@webapp.jsonp
def publish():
    types = request.json.get("types", [])
    map = app.config.get("ESDAO_ROLLING_PLUGINS", {})
    for t in types:
        klazz = plugin.load_class(map.get(t))
        klazz.publish()
    return ""


@blueprint.route('/rollback', methods=['POST'])
@webapp.jsonp
def rollback():
    types = request.json.get("types", [])
    map = app.config.get("ESDAO_ROLLING_PLUGINS", {})
    for t in types:
        klazz = plugin.load_class(map.get(t))
        klazz.rollback()
    return ""