from octopus.core import app

class CRUDObject(object):

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

    def update(self, data):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()


class ES_CRUD_Wrapper(CRUDObject):

    INNER_TYPE = None

    def __init__(self, raw=None):
        if raw is not None:
            # remove any disallowed fields
            pass

        self.inner = self.INNER_TYPE(raw)

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

    def update(self, data):
        self.inner = self.INNER_TYPE(data)

    def delete(self):
        self.inner.delete()