from octopus.modules.sheets.core import StructuralSheet
from octopus.lib import strings
from octopus.lib.coerce import CoerceFactory
from copy import deepcopy
import types

class NoReaderException(Exception):
    pass

class NoWriterException(Exception):
    pass

class ObjectByRow(StructuralSheet):
    def __init__(self, reader=None, writer=None, spec=None, auto_read=True):
        """
        Spec is of the following form:

        {
            "columns" : [
                {
                    "col_name" : "<name as it appears in the sheet>",
                    "trim" : "<whether to whitespace trim>",
                    "normalised_name" : "<normalised name of the column>",
                    "default" : "<default value if not set or set to the empty string>",
                    "coerce" : ["<name of coerce function>"],
                    "ignore_values" : ["<values that should be treated as empty string>"],
                    "to_unicode" : "<name of coerce function which will turn the coerced value back to unicode>"
                }
            ]
        }

        :param reader:
        :param spec:
        :param auto_read:
        :return:
        """
        self.reader = reader
        self.writer = writer
        self.spec = spec

        self.raw_col_spec = []
        self.compiled_col_spec = {}
        self.name_map = {}
        self.column_ordering = []
        self.data = None

        self._is_read = False

        if spec is not None:
            for s in spec.get("columns", []):
                self.add_col_spec(**s)

        if auto_read and self.reader is not None:
            self.read()

    ####################################################
    ## StructuralSheet overrides

    def read(self):
        if self._is_read:
            return

        if self.reader is None:
            raise NoReaderException("You have attempted to call 'read' on an object with no reader specified.")

        # read the data out of the reader
        raw = self.reader.read()

        # create our internal dataset that we'll read from the raw layer
        self.data = []

        # take the first row as the header row, and translate it
        headers = raw.lpop()
        new_headers = [self.name_map.get(x) for x in headers if x in self.name_map]

        # set the headers on the raw dataset too, so we can build a dict on it
        raw.headers = [self.name_map.get(x, x) for x in headers]

        dicts = raw.dict    # an ordered dict
        raw.wipe()
        for d in dicts:
            new_dict = {}
            empty_row = True
            for k in d.keys():
                spec = self.compiled_col_spec.get(k)
                if spec is not None:
                    nv = self._apply_spec(d[k], spec)
                    new_dict[k] = nv
                    if nv is not None:
                        empty_row = False
            if not empty_row:
                self.data.append(new_dict)

        self._is_read = True

    def write(self, close=True):
        """
        Write and close the file.
        """
        if self.writer is None:
            raise NoWriterException("You have attempted to call 'write' on an object with no writer specified.")

        # build a table to return
        rows = []

        # set the header row
        current_row = []
        for cn in self.column_ordering:
            spec = self.compiled_col_spec.get(cn)
            current_row.append(spec.get("col_name"))
        rows.append(current_row)

        # go through each object, and output the results in the correct column order
        for obj in self.data:
            current_row = []
            for cn in self.column_ordering:
                spec = self.compiled_col_spec.get(cn)
                to_unicode = spec.get("to_unicode")
                val = obj.get(cn)
                if val is not None:
                    val = to_unicode(val)
                else:
                    val = u""
                current_row.append(val)
            rows.append(current_row)

        self.writer.write(rows, close=close)

    def dicts(self):
        return self.data

    def dataobj_struct(self):
        fields = {}
        for s in self.raw_col_spec:
            cs = s.get("coerce", ["unicode"])
            if len(cs) > 0:
                c = cs[len(cs) - 1]
                fields[s.get("normalised_name")] = {"coerce" : c}
            else:
                fields[s.get("normalised_name")] = {}
        struct = { "fields" : fields }
        return struct

    ####################################################
    ## Methods specific to this sheet type

    def add_col_spec(self, col_name, trim=True, normalised_name=None, default=None, coerce=None, ignore_values=None, to_unicode=None):
        coerce = coerce if coerce is not None else []
        ignore_values = ignore_values if ignore_values is not None else []

        # coerce all the values
        uc = CoerceFactory.get("unicode")
        col_name = uc(col_name)

        # the elements which are stored exactly as they are provided
        raw = {
            "col_name" : col_name,
            "trim" : trim,
            "default" : default,
        }

        # the normalised name for the column
        if normalised_name is None:
            norm = self._normalise(col_name)
            names = self.name_map.values()
            if norm in names:
                i = 1
                while True:
                    pnh = norm + str(i)
                    if pnh not in names:
                        raw["normalised_name"] = pnh
                        break
            else:
                raw["normalised_name"] = norm
        else:
            raw["normalised_name"] = normalised_name

        # the list of coerce functions (by name)
        if len(coerce) == 0:
            raw["coerce"] = []
        else:
            named = [c if isinstance(c, basestring) else c.func_name for c in coerce]
            raw["coerce"] = named

        # the list of ignore values
        if len(ignore_values) == 0:
            raw["ignore_values"] = []
        else:
            raw["ignore_values"] = ignore_values

        if to_unicode is None:
            raw["to_unicode"] = "unicode"
        else:
            raw["to_unicode"] = to_unicode

        # now compile the spec
        comp = deepcopy(raw)
        funcs = [f if type(f) == types.FunctionType else CoerceFactory.get(f) for f in coerce]
        comp["coerce"] = funcs
        comp["to_unicode"] = raw["to_unicode"] if type(raw["to_unicode"]) == types.FunctionType else CoerceFactory.get(raw["to_unicode"])

        # now add them to the registers on the instance
        self.raw_col_spec.append(raw)
        self.compiled_col_spec[comp.get("normalised_name")] = comp
        self.name_map[comp.get("col_name")] = comp.get("normalised_name")
        self.column_ordering.append(comp.get("normalised_name"))

    ###################################################
    ## Internal methods

    def _normalise(self, col_name):
        return strings.normalise(col_name, ascii=True, unpunc=True, lower=True, spacing=True, strip=True, space_replace="_")

    def _apply_spec(self, val, spec):
        # first apply any transformations that may make the value become the empty string
        if val is not None:
            if spec.get("trim", True):
                val = val.strip()

            if val in spec.get("ignore_values", []):
                val = ""

        # now if the value is none or the empty string, return the default value
        if val is None or val == "":
            return spec.get("default")

        # apply the coerce functions in order
        for c in spec.get("coerce", []):
            val = c(val)

        return val
