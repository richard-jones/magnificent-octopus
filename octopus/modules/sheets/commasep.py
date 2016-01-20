from octopus.core import app
from octopus.modules.sheets.core import BaseReader, BaseWriter, FileReadException, DataStructureException
import csv, codecs, tablib

class CsvReader(BaseReader):

    DIALECTS = {
        "excel" : csv.excel
    }

    def __init__(self, path, input_encoding=None, try_other_encodings=True, fallback_encodings=None, input_dialect=None):
        super(CsvReader, self).__init__(path)

        self.try_other_encodings = try_other_encodings
        self.input_encoding = input_encoding if input_encoding is not None else app.config.get("CSV_READER_INPUT_ENCODING", "utf-8")
        self.fallback_encodings = fallback_encodings if fallback_encodings is not None else app.config.get("CSV_READER_FALLBACK_ENCODINGS", ["cp1252", "cp1251", "iso-8859-1", "iso-8859-2", "windows-1252", "windows-1251", "mac_roman"])
        self.input_dialect = input_dialect if input_dialect is not None else self.DIALECTS.get(app.config.get("CSV_READER_INPUT_DIALECT", "excel"), csv.excel)

    def read(self):
        if self.path is not None:
            encodings = [self.input_encoding]
            if self.try_other_encodings:
                encodings += self.fallback_encodings
            for enc in encodings:
                with codecs.open(self.path, 'r+b', encoding=enc) as f:
                    try:
                        self._read_from_file(f)
                        return self.data
                    except FileReadException as e:
                        continue
                    except DataStructureException as e:
                        continue

            raise FileReadException("Unable to find a character encoding which reads the file into a legitimate data structure")

        elif self.file is not None:
            self._read_from_file(self.file)
            return self.data

    def _read_from_file(self, file_object):
        """
        Retrieve all of the information from the stored file using standard csv lib
        :return: Entire CSV contents, a list of rows (like the standard csv lib)
        """
        try:
            if file_object.closed:
                file_object = codecs.open(file_object.name, 'r+b', encoding=self.input_encoding)

            reader = UnicodeReader(file_object, dialect=self.input_dialect)
            length = -1
            self.data = tablib.Dataset()
            for row in reader:
                if length == -1:
                    length = len(row)
                if len(row) != length:
                    raise DataStructureException("Unable to read file into meaningful datastructure using encoding {x}".format(x=self.input_encoding))
                if self._is_empty(row):
                    continue
                self.data.append(row)
        except:
            raise FileReadException("Unable to read file with encoding {x} - likely an encoding problem".format(x=self.input_encoding))

    def _is_empty(self, row):
        return sum([1 if c is not None and c != "" else 0 for c in row]) == 0

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, **kwds):
        f = UTF8Recoder(f)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f):
        self.reader = f

    def __iter__(self):
        return self

    def next(self):
        val = self.reader.next()
        raw = val.encode("utf-8")
        if raw.startswith(codecs.BOM_UTF8):
            raw = raw.replace(codecs.BOM_UTF8, '', 1)
        return raw

class CsvWriter(BaseWriter):
    def write(self, *args, **kwargs):
        pass
