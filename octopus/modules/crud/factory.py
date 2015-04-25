from octopus.core import app
from octopus.lib import plugin

class CRUDFactory(object):

    @classmethod
    def get_class(cls, container_type, operation=None):
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

        if operation is not None:
            # determine if the operation is permitted
            if operation not in ct:
                return None
            if not ct.get(operation).get("enable", False):
                return None

        return plugin.load_class(m)
