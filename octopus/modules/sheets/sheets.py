from octopus.modules.sheets.core import StructuralSheet
from octopus.lib import strings
from octopus.lib.coerce import CoerceFactory
import tablib
from copy import deepcopy
import types

class ObjectByRow(StructuralSheet):
    def __init__(self, reader, spec=None):
        """
        Spec is of the following form:

        [
            {
                "col_name" : "<name as it appears in the sheet>",
                "trim" : "<whether to whitespace trim>",
                "normalised_name" : "<normalised name of the column>",
                "default" : "<default value if not set or set to the empty string>",
                "coerce" : ["<name of coerce function>"],
                "ignore_values" : ["<values that should be treated as empty string>"]
            }
        ]

        :param reader:
        :param spec:
        :return:
        """
        self.reader = reader

        self.raw_spec = []
        self.compiled_spec = {}
        self.name_map = {}

        self.data = None

        if spec is not None:
            for s in spec:
                self.add_spec(**s)

    def read(self):
        # read the data out of the reader
        raw = self.reader.read()

        # create our internal dataset that we'll read from the raw layer
        self.data = tablib.Dataset()

        # take the first row as the header row, and translate it
        headers = raw.lpop()
        new_headers = [self.name_map.get(x) for x in headers if x in self.name_map]
        self.data.headers = new_headers

        # set the headers on the raw dataset too, so we can build a dict on it
        raw.headers = [self.name_map.get(x, x) for x in headers]

        dicts = raw.dict    # an ordered dict
        raw.wipe()
        for d in dicts:
            new_values = []
            for k in d.keys():
                spec = self.compiled_spec.get(k)
                if spec is not None:
                    nv = self._apply_spec(d[k], spec)
                    new_values.append(nv)
            if len(new_values) > 0:
                self.data.append(new_values)

    def dicts(self):
        headers = self.data.headers
        for i in range(self.data.height):
            vals = self.data[i]
            obj = {}
            for j in range(len(headers)):
                obj[headers[j]] = vals[j]
            yield obj

    def add_spec(self, col_name, trim=True, normalised_name=None, default=None, coerce=None, ignore_values=None):
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
        if coerce is None:
            raw["coerce"] = []
        else:
            named = [c if isinstance(c, basestring) else c.func_name for c in coerce]
            raw["coerce"] = named

        # the list of ignore values
        if ignore_values is None:
            raw["ignore_values"] = []
        else:
            raw["ignore_values"] = ignore_values

        # now compile the spec
        comp = deepcopy(raw)
        funcs = [f if type(f) == types.FunctionType else CoerceFactory.get(f) for f in coerce]
        comp["coerce"] = funcs

        # now add them to the registers on the instance
        self.raw_spec.append(raw)
        self.compiled_spec[comp.get("normalised_name")] = comp
        self.name_map[comp.get("col_name")] = comp.get("normalised_name")

    def dataobj_struct(self):
        fields = {}
        for s in self.raw_spec:
            cs = s.get("coerce", ["unicode"])
            c = cs[len(cs) - 1]
            fields[s.get("normalised_name")] = {"coerce" : c}
        struct = { "fields" : fields }
        return struct

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
