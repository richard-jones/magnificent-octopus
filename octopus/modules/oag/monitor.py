from flask import Blueprint, render_template, abort

from octopus.core import app
from octopus.modules.oag.dao import JobsDAO

blueprint = Blueprint('oagmonitor', __name__)

# show the index page for monitoring the jobs
@blueprint.route('/', methods=['GET','POST'])
def index():
    return render_template("oagmonitor/index.html")

# individual page for a job state
@blueprint.route('/job/<job_id>', methods=['GET'])
def job(job_id):
    j = JobsDAO.pull(job_id)
    if j is None:
        abort(404)
    state = j.state()
    return render_template("oagmonitor/state.html", state=state, job=j)