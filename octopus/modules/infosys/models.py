from octopus.lib import dataobj, plugin
from octopus.modules.es import dao
from copy import deepcopy
from octopus.core import app
from octopus.modules.crud.models import CRUDObject

from objectpath import Tree
import types

class InfoSysException(Exception):
    pass

class InfoSysModel(dataobj.DataObj, dao.ESInstanceDAO):
    __type__ = None

    def __init__(self, type=None, full_struct=None, record_struct=None, admin_struct=None, index_rules=None, full=None, record=None, admin=None, *args, **kwargs):
        # first set the data model up with the full document struct
        if full_struct is None:
            full_struct = {
                "fields" : {
                    "id" : {"coerce" : "unicode"},
                    "created_date" : {"coerce" : "utcdatetime"},
                    "last_updated" : {"coerce" : "utcdatetime"}
                },
                "objects" : [],
                "structs" : {}
            }

            # now add the record and admin structs
            if record_struct is not None:
                full_struct["objects"].append("record")
                full_struct["structs"]["record"] = record_struct

            if admin_struct is not None:
                full_struct["objects"].append("admin")
                full_struct["structs"]["admin"] = admin_struct

            # now convert the index rules to a struct and add that
            if index_rules is not None:
                index_struct = self._index_rules_to_struct(index_rules)
                full_struct["objects"].append("index")
                full_struct["structs"]["index"] = index_struct

        self._add_struct(full_struct)

        # now determine if there is a raw record to pass up
        nkwargs = deepcopy(kwargs)
        if full is not None:
            raw = deepcopy(full)
            if "index" in raw:
                del raw["index"]
            nkwargs["raw"] = raw
        else:
            raw = {}
            if record is not None:
                raw["record"] = record
            if admin is not None:
                raw["admin"] = admin
            if len(raw.keys()) > 0:
                nkwargs["raw"] = raw

        # now kick this up to the super classes.  We can't set any properties on this object
        # until after that is done
        super(InfoSysModel, self).__init__(*args, **nkwargs)

        # a member variable to store our object's properties
        # use a dictionary to minimise the impact on the keys that cannot
        # be read/written to the dataobj
        self._info_sys_properties = {}

        self._info_sys_properties["full_struct"] = full_struct
        self._info_sys_properties["record_struct"] = record_struct
        self._info_sys_properties["admin_struct"] = admin_struct
        self._info_sys_properties["index_rules"] = index_rules if index_rules is not None else []
        self._info_sys_properties["type"] = type
        self._info_sys_properties["args"] = args
        self._info_sys_properties["kwargs"] = kwargs

    def _index_rules_to_struct(self, index_rules):
        fields = {}
        for rule in index_rules:
            field = rule.get("index_field")
            struct_args = rule.get("struct_args", {})
            fields[field] = struct_args

        return {"fields" : fields}

    def _make_instance(self, obj):
        return self.__class__(type=type, full_struct=self._info_sys_properties.get("full_struct"), full=obj, *self._info_sys_properties.get("args", []), **self._info_sys_properties.get("kwargs"))

    def _get_write_type(self, raise_if_not_set=False):
        type = self._info_sys_properties.get("type")
        if type is None:
            raise InfoSysException("No 'type' set on InfoSysModel instance")
        return type

    def _get_read_types(self, raise_if_not_set=False):
        type = self._info_sys_properties.get("type")
        if type is None:
            raise InfoSysException("No 'type' set on InfoSysModel instance")
        return [type]

    ##########################################################
    ## Standard getters and setters for this object

    @property
    def record(self):
        return self._get_single("record")

    @record.setter
    def record(self, val):
        """
        type, struct, instructions = dataobj.construct_lookup("record", self._struct)
        dataobj.construct(val, struct, self._coerce_map)
        kwargs = dataobj.construct_kwargs(type, "set", instructions)
        self._set_single("record", val, **kwargs)
        """
        self._set_with_struct("record", val)

    @property
    def admin(self):
        return self._get_single("admin")

    @admin.setter
    def admin(self, val):
        self._set_with_struct("admin", val)

    def objectpath(self, path):
        t = Tree(self.data)
        gen = t.execute(path)
        vals = None
        if gen is not None:
            if isinstance(gen, types.GeneratorType):
                vals = [x for x in gen]
            elif isinstance(gen, list):
                return gen
            else:
                vals = [gen]
        return vals

    ##########################################################
    ## storage methods which mimic the class-method instances in
    ## a concrete ESDAO instance

    def pull(self, id, conn=None):
        type = self._get_read_types(True)
        obj = dao.ESDAO.pull(id, conn=conn, wrap=False, types=type)
        if obj is not None:
            return self._make_instance(obj)
        return None

    def query(self, q='', terms=None, should_terms=None, facets=None, conn=None, **kwargs):
        type = self._get_read_types(True)
        return dao.ESDAO.query(q=q, terms=terms, should_terms=should_terms, facets=facets, conn=conn, types=type, **kwargs)

    def scroll(self, q=None, page_size=1000, limit=None, keepalive="1m", conn=None, raise_on_scroll_error=True):
        type = self._get_read_types(True)
        for o in dao.ESDAO.scroll(q=q, page_size=page_size, limit=limit, keepalive=keepalive, conn=conn, raise_on_scroll_error=raise_on_scroll_error, types=type, wrap=False):
            yield self._make_instance(o)

    def delete_by_query(self, query, conn=None, es_version="0.90.13"):
        type = self._get_write_type(True)
        dao.ESDAO.delete_by_query(query, conn=conn, es_version=es_version, type=type)

    def object_query(self, q='', terms=None, should_terms=None, facets=None, conn=None, **kwargs):
        type = self._get_read_types(True)
        return [self._make_instance(obj) for obj in dao.ESDAO.object_query(q=q, terms=terms, should_terms=should_terms, facets=facets, conn=conn, types=type, wrap=False, **kwargs)]

    def iterate(self, q, page_size=1000, limit=None, **kwargs):
        type = self._get_read_types(True)
        for o in dao.ESDAO.iterate(q=q, page_size=page_size, limit=limit, wrap=False, types=type, **kwargs):
            yield self._make_instance(o)

    def iterall(self, page_size=1000, limit=None, **kwargs):
        type = self._get_read_types(True)
        for o in dao.ESDAO.iterall(page_size=page_size, limit=limit, types=type, wrap=False, **kwargs):
            yield self._make_instance(o)

    def count(self, q, **kwargs):
        type = self._get_read_types(True)
        return dao.ESDAO.count(q=q, types=type, **kwargs)

    ############################################################
    ## overrides of instance methods

    def prep(self):
        for r in self._info_sys_properties.get("index_rules", []):
            fd = r.get("function", {})
            func_path = app.config.get("INDEX_FUNCTIONS_MODULE") + "." + fd.get("name")
            fn = plugin.load_function(func_path)
            idx = fn(self.data, *fd.get("args", []), **fd.get("kwargs", {}))
            if idx is not None:
                path = "index." + r.get("index_field")
                if isinstance(idx, list):
                    self._set_list(path, idx)
                else:
                    self._set_single(path, idx)

    def delete(self, conn=None, type=None):
        if type is None:
            type = self._get_write_type(True)
        super(InfoSysModel, self).delete(conn=conn, type=type)

    def save(self, conn=None, blocking=False, **kwargs):
        type = self._get_write_type(True)
        super(InfoSysModel, self).save(conn=conn, blocking=blocking, type=type, **kwargs)

class InfoSysCrud(CRUDObject):
    pass