class FileReadException(Exception):
    pass

class DataStructureException(Exception):
    pass

class BaseReader(object):
    def __init__(self, path, *args, **kwargs):
        self.file = None
        self.path = None

        if hasattr(path, "read"):
            self.file = path
        else:
            self.path = path
        super(BaseReader, self).__init__(*args, **kwargs)

    def read(self, *args, **kwargs):
        pass

class BaseWriter(object):
    def __init__(self, path, *args, **kwargs):
        self.file = None
        self.path = None

        if hasattr(path, "write"):
            self.file = path
        else:
            self.path = path
        super(BaseWriter, self).__init__(*args, **kwargs)

    def write(self, rows, *args, **kwargs):
        pass

class StructuralSheet(object):
    def read(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass

    def dicts(self):
        """
        A list of python dicts represented by this object

        :return:
        """
        pass

    def set_dicts(self, data):
        """
        Set a list of dictionary objects to be represented by this object.

        They may be validated against the spec
        :param data:
        :return:
        """
        pass

    def dataobj_struct(self):
        """
        Get the struct for the dataobj produced by this sheet

        :return:
        """
        pass

