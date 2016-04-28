from octopus.lib import dataobj

EDGES_STRUCT = {
    "fields" : {
        "size" : {"coerce" : "integer"},
        "from" : {"coerce" : "integer"}
    },
    "lists" : {
        "sort" : {"contains" : "object"}
    },
    "objects" : [
        "query",
        "aggs",
        "aggregations"
    ],
    "required" : ["query"]
}

class QuerySanitisationException(Exception):
    pass

def sanitise(raw_query, struct, coerce_map=None, source_includes=None, aggs_type_field_map=None, sortable=None):
    """

    for sanitising aggregations, the following definition is used

    {
        "<aggregation type>" : {
            "<allowed field>" : {
                "nested_aggs" : True|False,
                "type_field_map" : {
                    ... structure repeats ...
                }
            }
        }
    }

    :param raw_query:
    :param struct:
    :param coerce_map:
    :param source_includes:
    :param aggs_type_field_map:
    :return:
    """
    if coerce_map is None:
        coerce_map = dataobj.DataObj.DEFAULT_COERCE
    try:
        clean_query = dataobj.construct(raw_query, struct, coerce_map, silent_prune=True)
    except dataobj.DataStructureException as e:
        raise QuerySanitisationException(e)

    topqkey = clean_query["query"].keys()[0]
    if topqkey not in ["filtered", "match_all"]:
        raise QuerySanitisationException("must be a filtered or match_all query")

    if source_includes is not None:
        clean_query["_source"] = {}
        clean_query["_source"]["includes"] = source_includes

    aggs = None
    if "aggs" in clean_query:
        aggs = clean_query["aggs"]
    elif "aggregations" in clean_query:
        aggs = clean_query["aggregations"]

    if aggs_type_field_map is not None and aggs is not None:
        removes = []
        for name, definition in aggs.iteritems():
            sane = _sanitise_aggregation(definition, aggs_type_field_map)
            if not sane:
                removes.append(name)

        for r in removes:
            del aggs[r]

        if len(aggs) == 0:
            if "aggs" in clean_query:
                del clean_query["aggs"]
            if "aggregations" in clean_query:
                del clean_query["aggregations"]


    if sortable is not None:
        if "sort" in clean_query:
            rmidx = []
            for i in range(len(clean_query["sort"])):
                so = clean_query["sort"][i]
                field = so.keys()[0]
                if field not in sortable:
                    rmidx.append(i)
            rmidx.sort(reverse=True)
            for idx in rmidx:
                del clean_query["sort"][idx]
    else:
        if "sort" in clean_query:
            del clean_query["sort"]

    return clean_query


def _sanitise_aggregation(definition, type_field_map):
    type = definition.keys()[0]
    field = definition[type].get("field")
    allowed_fields = type_field_map[type].keys()
    if field not in allowed_fields:
        return False

    subaggs = None
    if "aggs" in definition:
        subaggs = definition["aggs"]
    elif "aggregations" in definition:
        subaggs = definition["aggregations"]

    if subaggs is None:
        return True

    allowed_subaggs = type_field_map[type][field].get("aggs", False)
    if not allowed_subaggs:
        if "aggs" in definition:
            del definition["aggs"]
        if "aggregations" in definition:
            del definition["aggregations"]

    stfm = type_field_map[type][field].get("type_field_map", {})

    removes = []
    for name, subdef in subaggs.iteritems():
        sane = _sanitise_aggregation(subdef, stfm)
        if not sane:
            removes.append(name)
    for r in removes:
        del subaggs[r]

    if len(subaggs) == 0:
        if "aggs" in definition:
            del definition["aggs"]
        if "aggregations" in definition:
            del definition["aggregations"]

    return True