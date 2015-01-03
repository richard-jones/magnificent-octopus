from flask import Blueprint, render_template

from octopus.core import app

blueprint = Blueprint('oagmonitor', __name__)

# show the index page for monitoring the jobs
@blueprint.route('/', methods=['GET','POST'])
def index():
    return render_template("oagmonitor/index.html")