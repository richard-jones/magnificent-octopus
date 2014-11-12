from octopus.core import app

from flask import Blueprint, render_template

blueprint = Blueprint('examples', __name__)

#@blueprint.route("/")
#def list_examples():
#    return render_template("examples/list.html")

@blueprint.route("/ac")
def autocomplete():
    return render_template("examples/es/autocomplete.html")

@blueprint.route("/fact")
def fact():
    return render_template("examples/sherpafact/proxy.html")

@blueprint.route("/clientjs")
def clientjs():
    pass

@blueprint.route("/epmc")
def epmc():
    pass

@blueprint.route("/romeo")
def romeo():
    # at the moment the romeo endpoint only deals with downloads, which is not very demoable
    pass

