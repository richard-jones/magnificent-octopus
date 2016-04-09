def compile(expr):
    comp = {"uncompiled_expression" : expr}

    mode = "path"
    path = ""
    filter = ""
    context = comp

    # first pass compilation
    for c in expr:
        if mode == "path":
            if "path" not in context:
                context["path"] = []

            if c not in ["[", "."]:
                path += c
                continue
            elif c == ".":
                if path != "":
                    context["path"].append(path)
                    path = ""
                continue
            elif c == "[":
                context["path"].append(path)
                mode = "filter"
                path = ""
                continue

        if mode == "filter":
            if c != "]":
                filter += c
                continue
            elif c == "]":
                mode = "path"
                comp["uncompiled_filter"] = filter
                filter = ""
                comp["then"] = {}
                context = comp["then"]
                continue

    # read out any remaining data
    if mode == "path" and path != "":
        context["path"].append(path)
    elif mode == "filter" and filter != "":
        context["uncompiled_filter"] = filter

    # now go through the compiled structure and compile any uncompiled filters
    _compile_filters(comp)

    return comp

def _compile_filters(comp):
    filter = None
    for k, v in comp.iteritems():
        if k == "uncompiled_filter":
            filter = _compile_filter(comp["uncompiled_filter"])
        elif k == "then":
            _compile_filters(comp["then"])
    if filter is not None:
        comp["filter"] = filter

def _compile_filter(expr):
    comp = {}

    mode = "path"
    path = ""
    context = comp

    for c in expr:
        if mode == "path":
            if "path" not in context:
                context["path"] = []

            if c not in ["=", "<", ">", "."]:
                path += c
                continue
            elif c == ".":
                if path != "":
                    context["path"].append(path)
                    path = ""
                continue
            elif c in ["=", "<", ">"]:
                context["path"].append(path)
                mode = "comparison"
                path = ""
                # do not continue - we need this picked up by the next block

        if mode == "comparison":
            if "comparison" not in comp:
                comp["comparison"] = ""

            if c == "=":
                if comp["comparison"] == "lt":
                    comp["comparison"] = "lte"
                elif comp["comparison"] == "gt":
                    comp["comparison"] = "gte"
                else:
                    comp["comparison"] = "eq"
                continue

            elif c == "<":
                comp["comparison"] = "lt"
                continue
            elif c == ">":
                comp["comparison"] = "gt"
                continue
            else:
                mode = "value"
                # again, do not continue - we need this picked up by the next block

        if mode == "value":
            if "value" not in comp:
                comp["value"] = ""
            comp["value"] += c

    if comp["value"].startswith("'"):
        comp["value"] = comp["value"][1:]
    if comp["value"].endswith("'"):
        comp["value"] = comp["value"][:-1]

    return comp

def apply(expr, doc):
    comp = compile(expr)