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
            "from_row" : 0,
            "to_row" : -1,
            "from_col" : 0,
            "to_col" : -1,
            "ignore_empty_rows" : True,
            "defaults" : {
                "on_coerce_failure" : "ignore|raise"
            },
            "columns" : [
                {
                    "col_name" : "<name as it appears in the sheet>",
                    "trim" : "<whether to whitespace trim: True|False>",
                    "normalised_name" : "<normalised name of the column>",
                    "default" : "<default value if not set or set to the empty string>",
                    "coerce" : ["<name of coerce function>"],
                    "ignore_values" : ["<values that should be treated as empty string>"],
                    "on_coerce_failure" : "ignore|raise",
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
        self.off_spec_data = None

        self._is_read = False

        if "from_row" not in self.spec:
            self.spec["from_row"] = 0
        if "to_row" not in self.spec:
            self.spec["to_row"] = -1
        if "from_col" not in self.spec:
            self.spec["from_col"] = 0
        if "to_col" not in self.spec:
            self.spec["to_col"] = -1
        if "ignore_empty_rows" not in self.spec:
            self.spec["ignore_empty_rows"] = True

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
        self.off_spec_data = []

        # take the first row as the header row
        headers = raw.pop(0)

        # go through the rows, translating them to a dictionary with the appropriate
        # data conversions
        for row in raw:
            if self._is_empty(row) and self.spec.get("ignore_empty_rows") is True:
                continue

            empty_row = True    # the above code catches initially empty rows, but once we've applied the spec a row may be empty too, so we need to catch that below
            on_spec = {}
            off_spec = {}
            for i in range(len(headers)):
                h = headers[i]
                val = row[i]
                sh = self.name_map.get(h)
                if sh is not None:
                    spec = self.compiled_col_spec.get(sh)
                    on_spec[sh] = self._apply_spec(val, spec)
                    if on_spec[sh] is not None and on_spec[sh] != "":
                        empty_row = False
                else:
                    off_spec[h] = val
                    if off_spec[h] is not None and off_spec[h] != "":
                        empty_row = False

            if not empty_row:
                self.data.append(on_spec)
                self.off_spec_data.append(off_spec)

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

    def set_dicts(self, data):
        self.data = []
        self.off_spec_data = []

        for d in data:
            on_spec = {}
            off_spec = {}
            for k in d.keys():
                spec = self.compiled_col_spec.get(k)
                if spec is not None:
                    on_spec[k] = d[k]
                else:
                    off_spec[k] = d[k]

            self.data.append(on_spec)
            self.off_spec_data.append(off_spec)

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

    def add_col_spec(self, col_name, trim=True, normalised_name=None, default=None, coerce=None, ignore_values=None, to_unicode=None, on_coerce_failure=None):
        coerce = coerce if coerce is not None else []
        ignore_values = ignore_values if ignore_values is not None else []

        if on_coerce_failure is None:
            on_coerce_failure = self.spec.get("defaults", {}).get("on_coerce_failure", "raise")

        # coerce all the values
        uc = CoerceFactory.get("unicode")
        col_name = uc(col_name)

        # the elements which are stored exactly as they are provided
        raw = {
            "col_name" : col_name,
            "trim" : trim,
            "default" : default,
            "on_coerce_failure" : on_coerce_failure
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
        funcs = [f if type(f) == types.FunctionType else CoerceFactory.get(f) for f in coerce if CoerceFactory.get(f) is not None]
        comp["coerce"] = funcs
        comp["to_unicode"] = raw["to_unicode"] if type(raw["to_unicode"]) == types.FunctionType else CoerceFactory.get(raw["to_unicode"])

        # now add them to the registers on the instance
        self.raw_col_spec.append(raw)
        self.compiled_col_spec[comp.get("normalised_name")] = comp
        self.name_map[comp.get("col_name")] = comp.get("normalised_name")
        self.column_ordering.append(comp.get("normalised_name"))

    def off_spec_dicts(self):
        return self.off_spec_data

    ###################################################
    ## Internal methods

    def _is_empty(self, row):
        return sum([1 if c is not None and c != "" else 0 for c in row]) == 0

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
            try:
                val = c(val)
            except:
                if spec.get("on_coerce_failure", "raise") == "raise":
                    print spec.get("normalised_name")
                    raise
                val = spec.get("default")

        return val
