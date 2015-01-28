from flask import Blueprint, abort

from octopus.core import app
from octopus.lib import plugin

blueprint = Blueprint('fragments', __name__)

@blueprint.route("/<frag_id>")
def fragment(frag_id):
    cfg = app.config.get("FRAGMENTS", {}).get(frag_id)
    fname = cfg.get("function")
    if fname is not None:
        fn = plugin.load_function(fname)
        return fn()
    abort(404)
