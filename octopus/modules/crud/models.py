from octopus.core import app

class CRUDObject(object):
    def __init__(self, raw=None, headers=None):
        pass

    @classmethod
    def pull(cls, id):
        raise NotImplementedError()

    @property
    def id(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def json(self):
        raise NotImplementedError()

    def update(self, data, headers=None):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()


class ES_CRUD_Wrapper(CRUDObject):

    INNER_TYPE = None

    def __init__(self, raw=None, headers=None):
        super(ES_CRUD_Wrapper, self).__init__(raw, headers)
        if raw is not None:
            # remove any disallowed fields
            pass

        self.inner = self.INNER_TYPE(raw)
        self.headers = headers

    @classmethod
    def pull(cls, id):
        inner = cls.INNER_TYPE.pull(id)
        if inner is None:
            return None
        this = cls()
        this.inner = inner
        return this

    @property
    def id(self):
        return self.inner.id

    def save(self):
        self.inner.save()

    def json(self):
        return self.inner.json()

    def update(self, data, headers=None):
        self.inner = self.INNER_TYPE(data)

    def delete(self):
        self.inner.delete()

class ES_CRUD_Wrapper_Ultra(ES_CRUD_Wrapper):
    """
    Same as ES_CRUD_Wrapper, but strips ids, created_date and last_updated as per
    normal expected behaviour.
    """
    def __init__(self, raw=None):
        if raw is not None:
            # remove any disallowed fields
            if "id" in raw:
                del raw["id"]
            if "created_date" in raw:
                del raw["created_date"]
            if "last_updated" in raw:
                del raw["last_updated"]

        super(ES_CRUD_Wrapper_Ultra, self).__init__(raw)

    def update(self, data, headers=None):
        # carry over the data from the old object
        data["id"] = self.inner.id
        data["created_date"] = self.inner.created_date

        # remove any disallowed fields
        if "last_updated" in data:
            del data["last_updated"]

        super(ES_CRUD_Wrapper_Ultra, self).update(data)