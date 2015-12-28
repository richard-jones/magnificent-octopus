class FileReadException(Exception):
    pass

class DataStructureException(Exception):
    pass

class BaseReader(object):
    def __init__(self, path, *args, **kwargs):
        self.file = None
        self.path = None

        if type(path) == file:
            self.file = path
        else:
            self.path = path
        super(BaseReader, self).__init__()

    def read(self, *args, **kwargs):
        pass

class BaseWriter(object):
    def __init__(self, path, *args, **kwargs):
        super(BaseWriter, self).__init__()

    def write(self, *args, **kwargs):
        pass

class StructuralSheet(object):
    def read(self, *args, **kwargs):
        pass

    def dicts(self):
        """
        A generator which produces python dictionary objects for each record

        :return:
        """
        pass

    def dataobj_struct(self):
        """
        Get the struct for the dataobj produced by this sheet

        :return:
        """
        pass

