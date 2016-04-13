from octopus.core import app
from octopus.modules.sheets.core import BaseReader, BaseWriter, FileReadException, DataStructureException
import csv, codecs, cStringIO

class CsvReader(BaseReader):

    DIALECTS = {
        "excel" : csv.excel
    }

    def __init__(self, path, input_encoding=None, try_other_encodings=True, fallback_encodings=None, input_dialect=None, rectangular=True):
        """
        Set up a csv reader around the specified path (which may also be a file object)

        :param path:    path to file, or file-like object
        :param input_encoding:  expected input encoding (set from config if not set here)
        :param try_other_encodings: if the expected input encoding doesn't work, should we try others
        :param fallback_encodings:  if we are trying other encodings, use this list  (set from config if not set here)
        :param input_dialect: name of the dialect.  Allowed values are "excel".  (set from config if not set here)
        :param rectangular: should the resulting csv be rectangular.  Usually this is true, and if a csv is not rectangular, it may indicate a failure to correctly interpret the encoding)
        :return:
        """
        super(CsvReader, self).__init__(path)

        self.try_other_encodings = try_other_encodings
        self.input_encoding = input_encoding if input_encoding is not None else app.config.get("CSV_READER_INPUT_ENCODING", "utf-8")
        self.fallback_encodings = fallback_encodings if fallback_encodings is not None else app.config.get("CSV_READER_FALLBACK_ENCODINGS", ["cp1252", "cp1251", "iso-8859-1", "iso-8859-2", "windows-1252", "windows-1251", "mac_roman"])
        self.input_dialect = input_dialect if input_dialect is not None else self.DIALECTS.get(app.config.get("CSV_READER_INPUT_DIALECT", "excel"), csv.excel)

        self.rectangular = rectangular

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
            self.data = []
            for row in reader:
                if length == -1:    # track the length of the first row - everything else needs to be the same length, or we'll throw an error
                    length = len(row)
                if len(row) != length and self.rectangular:
                    raise DataStructureException("Unable to read file into meaningful datastructure using encoding {x}".format(x=self.input_encoding))
                self.data.append(row)
        except:
            raise FileReadException("Unable to read file with encoding {x} - likely an encoding problem".format(x=self.input_encoding))

class CsvWriter(BaseWriter):
    def __init__(self, path, output_encoding=None):
        super(CsvWriter, self).__init__(path)

        self.output_encoding = output_encoding if output_encoding is not None else app.config.get("CSV_READER_OUTPUT_ENCODING", "utf-8")

    def write(self, rows, close=True, *args, **kwargs):
        """
        Write and close the file.
        """
        if self.path is not None:
            self.file = codecs.open(self.path, "wb", encoding=self.output_encoding)
        elif self.file is not None:
            if self.file.closed:
                self.file = codecs.open(self.file.name, "wb", encoding=self.output_encoding)
            else:
                self.file.seek(0)
                self.file.truncate()

        # Write new CSV data
        writer = UnicodeWriter(self.file, encoding=self.output_encoding)
        writer.writerows(rows)

        if close:
            self.file.close()

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

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.encoding = encoding

    def writerow(self, row):
        encoded_row = []
        for s in row:
            if s is None:
                s = ''
            if not isinstance(s, basestring):
                s = str(s)
            encoded_row.append(s.encode(self.encoding))
        self.writer.writerow(encoded_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
