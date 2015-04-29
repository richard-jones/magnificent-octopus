"""Get JSON from a Flask request. Needed only for apps using Flask older than 0.10. 0.10 has this method directly on the request object."""

import json


def _get_data(req):
    getter = getattr(req, 'get_data', None)
    if getter is not None:
        return getter()
    return req.data


def is_json(request):
        """Indicates if this request is JSON or not.  By default a request
        is considered to include JSON data if the mimetype is
        :mimetype:`application/json` or :mimetype:`application/*+json`.
        """
        mt = request.mimetype
        if mt == 'application/json':
            return True
        if mt.startswith('application/') and mt.endswith('+json'):
            return True
        return False


def get_json(flask_request, force=False, silent=False):
        """Parses the incoming JSON request data and returns it.
        By default this function will
        only load the json data if the mimetype is application/json
        but this can be overridden by the force parameter.
        :param force: if set to ``True`` the mimetype is ignored.
        :param silent: if set to ``True`` this method will fail silently
                       and return ``None``.
        """

        if not (force or is_json(flask_request)):
            return None

        # We accept a request charset against the specification as
        # certain clients have been using this in the past.  This
        # fits our general approach of being nice in what we accept
        # and strict in what we send out.
        request_charset = flask_request.mimetype_params.get('charset')
        try:
            data = _get_data(flask_request)
            if request_charset is not None:
                rv = json.loads(data, encoding=request_charset)
            else:
                rv = json.loads(data)
        except ValueError as e:
            if silent:
                rv = None
            else:
                rv = flask_request.on_json_loading_failed(e)
        return rv