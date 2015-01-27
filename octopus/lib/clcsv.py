import csv, codecs, re, os
import cStringIO

class CsvReadException(Exception):
    pass

class ClCsv():

    def __init__(self, file_path=None, writer=None,
                 output_encoding="utf-8", input_encoding="utf-8",
                 try_encodings_hard=True, fallback_input_encodings=None):
        """
        Class to wrap the Python CSV library. Allows reading and writing by column.
        :param file_path: A file object or path to a file. Will create one at specified path if it does not exist.
        """
        self.output_encoding = output_encoding
        self.input_encoding = input_encoding

        if fallback_input_encodings is None and try_encodings_hard:
            fallback_input_encodings = ["cp1252", "cp1251", "iso-8859-1", "iso-8859-2", "windows-1252", "windows-1251"]
        self.fallback_input_encodings = fallback_input_encodings

        # Store the csv contents in a list of tuples, [ (column_header, [contents]) ]
        self.data = []

        # Get an open file object from the given file_path or file object
        if file_path is not None:
            if type(file_path) == file:
                # NOTE: if you have passed in a file object, it MUST work - as in, it must be set to
                # read the right encoding, and everything.  We will not try to parse it again if it
                # fails the first time.  If it is closed, you will also need to be sure to set the input_encoding.
                # All round - better if you just give us the file path
                self.file_object = file_path
                if self.file_object.closed:
                    self.file_object = codecs.open(self.file_object.name, 'r+b', encoding=self.input_encoding)

                # explicitly read this file in
                self._read_file(self.file_object)
            else:
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    self._read_from_path(file_path)
                else:
                    # If the file doesn't exist, create it.
                    self.file_object = codecs.open(file_path, 'w+b', encoding=self.output_encoding)

        elif writer is not None:
            self.file_object = writer

    def _read_from_path(self, file_path):
        codes = [self.input_encoding] + self.fallback_input_encodings
        for code in codes:
            try:
                file_object = codecs.open(file_path, 'r+b', encoding=code)
                self._read_file(file_object)
                self.file_object = file_object
                self.input_encoding = code
                return
            except:
                pass
        # if we get to here, we were unable to read the file using any method
        raise CsvReadException("Unable to find a codec which can parse the file correctly")

    def _read_file(self, file_object):
        """
        Retrieve all of the information from the stored file using standard csv lib
        :return: Entire CSV contents, a list of rows (like the standard csv lib)
        """
        try:
            if file_object.closed:
                codecs.open(file_object.name, 'r+b', encoding=self.input_encoding)

            reader = UnicodeReader(file_object, output_encoding=self.output_encoding)
            rows = []
            for row in reader:
                rows.append(row)

            self._populate_data(rows)
            return rows
        except:
            raise CsvReadException("Unable to read file (possibly a codec problem, or a data structure problem)")

    def headers(self):
        """
        Return the headers of all of the columns in the csv in the order that they appear
        :return: just the headers
        """
        return [h for h, _ in self.data]

    def set_headers(self, headers):
        for h in headers:
            c = self.get_column(h)
            if c is None:
                self.set_column(h, [])

    def columns(self):
        """
        Iterate over the columns in the csv in the order that they appear
        :return: a generator which yields columns
        """
        headers = self.headers()
        for h in headers:
            col = self.get_column(h)
            yield col

    def objects(self):
        """
        Iterate over the rows in the csv in the order they are provided, returned
        as objects keyed by the header row
        :return: a generator which yields objects
        """
        _, c = self.get_column(0)
        size = len(c)
        headers = self.headers()
        for i in range(size):
            obj = {}
            for h in headers:
                _, col = self.get_column(h)
                val = col[i]
                obj[h] = val
            yield obj

    def add_object(self, obj):
        for h, c in self.columns():
            v = obj.get(h)
            if v is not None:
                c.append(v)
            else:
                c.append("")

    def get_column(self, col_identifier):
        """
        Get a column from the CSV file.
        :param col_identifier: An int column index or a str column heading.
        :return: The column, as a { heading : [contents] } dict.
        """
        try:
            if type(col_identifier) == int:
                # get column by index
                return self.data[col_identifier]
            elif isinstance(col_identifier, basestring):
                # get column by title
                for col in self.data:
                    if col[0] == col_identifier:
                        return col
        except IndexError:
            return None

    def set_column(self, col_identifier, col_contents):
        """
        Set a column in the CSV file.
        :param col_identifier: An int column index or a str column heading.
        :param col_contents: The contents for the column
        """
        try:
            if type(col_identifier) == int:
                self.data[col_identifier] = col_contents
            elif isinstance(col_identifier, basestring):
                # set column by title.
                num = self.get_colnumber(col_identifier)
                if num is not None and type(col_contents) == list:
                    self.set_column(num, (col_identifier, col_contents))
                else:
                    raise IndexError

        except IndexError:
            # The column isn't there already; append a new one
            if type(col_identifier) == int:
                self.data.append(col_contents)
            elif isinstance(col_identifier, basestring):
                self.data.append((col_identifier, col_contents))

    def get_colnumber(self, header):
        """
        Return the column number of a given header
        :param header:
        :return: The column number
        """
        for i in range(0, len(self.data)):
            if self.data[i][0] == header:
                return i
        return None

    def get_rownumber(self, first_col_val):
        """
        Get the row number of a given first column value, or none if not found
        :param first_col_val:
        :return: The row number
        """

        try:
            (col_name, col_contents) = self.data[0]
            col_data = [col_name] + col_contents
            return col_data.index(first_col_val)
        except ValueError:
            return None

    def save(self, close=True):
        """
        Write and close the file.
        """
        rows = []
        # find out how many rows we're going to need to write
        max_rows = 0
        for _, cont in self.data:
            if len(cont) > max_rows:
                max_rows = len(cont)
        max_rows += 1 # add the header row

        for i in range(0, max_rows):
            row = []
            for (col_name, col_contents) in self.data:
                col_data = [col_name] + col_contents
                if len(col_data) > i:
                    row.append(col_data[i])
                else:
                    row.append("")
            rows.insert(i, row)

        # Remove current contents of file
        self.file_object.seek(0)
        self.file_object.truncate()

        # Write new CSV data
        writer = UnicodeWriter(self.file_object, encoding=self.output_encoding)
        writer.writerows(rows)

        if close:
            self.file_object.close()

    def _populate_data(self, csv_rows):
        # Reset the stored data
        self.data = []
        if len(csv_rows) == 0:
            return

        # Add new data
        for i in range(0, len(csv_rows[0])):
            col_data = []
            for row in csv_rows[1:]:
                col_data.append(row[i])
            self.data.append((csv_rows[0][i], col_data))

class BadCharReplacer:
    """
    Iterator that reads an encoded stream and replaces Bad Characters!

    The underlying reader MUST be returning UTF-8 encoded unicode strings
    """
    def __init__(self, f, charmap=None):
        self.reader = f

        self.charmap = charmap
        if self.charmap is None:
            self.charmap = {
                # unicode versions
                #'\xc2\x82' : ',',        # High code comma
                #'\xc2\x84' : ',,',       # High code double comma
                '\xc2\x85' : '...',      # Tripple dot
                #'\xc2\x88' : '^',        # High carat
                #'\xc2\x91' : '\x27',     # Forward single quote
                #'\xc2\x92' : '\x27',     # Reverse single quote
                #'\xc2\x93' : '\x22',     # Forward double quote
                #'\xc2\x94' : '\x22',     # Reverse double quote
                #'\xc2\x95' : ' ',
                #'\xc2\x96' : '-',        # High hyphen
                #'\xc2\x97' : '--',       # Double hyphen
                #'\xc2\x99' : ' ',
                #'\xc2\xa0' : ' ',
                #'\xc2\xa6' : '|',        # Split vertical bar
                #'\xc2\xab' : '<<',       # Double less than
                #'\xc2\xbb' : '>>',       # Double greater than
                #'\xc2\xbc' : '1/4',      # one quarter
                #'\xc2\xbd' : '1/2',      # one half
                #'\xc2\xbe' : '3/4',      # three quarters
                #'\xca\xbf' : '\x27',     # c-single quote
                #'\xcc\xa8' : '',         # modifier - under curve
                #'\xcc\xb1' : '',         # modifier - under line
            }

        self.pattern = '(' + '|'.join(self.charmap.keys()) + ')'
        self.rx = re.compile(self.pattern)

    def __iter__(self):
        return self

    def next(self):
        val = self.reader.next()

        def replace_chars(match):
            # this function returns the substitute value from the dict above
            char = match.group(0)
            return self.charmap[char]

        # if the rx does match, then do the substitution.  I think this is the fastest
        # way to do this
        if self.rx.search(val) is not None:
            return self.rx.sub(replace_chars, val)

        # if no match, return the unmodifed string
        return val

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = f # codecs.getreader("ISO-8859-2")(f) # FIXME: just for testing
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        val = self.reader.next()
        return val.encode(self.encoding)

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, output_encoding="utf-8", **kwds):
        self.output_encoding = output_encoding
        f = UTF8Recoder(f, self.output_encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, self.output_encoding) for s in row]

    def __iter__(self):
        return self

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
