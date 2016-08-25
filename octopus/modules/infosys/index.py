"""
Functions which are asked to produce values from provided documents to be included
in the indexing field.

All functions will receive the raw python object as the first argument, and then the
arguments and keyword arguments as specified by the caller
"""

from objectpath import Tree
import types
from octopus.lib import strings

def _execute(tree, expr):
    vals = None
    gen = tree.execute(expr)
    if gen is not None:
        if isinstance(gen, types.GeneratorType):
            vals = [x for x in gen]
        elif isinstance(gen, list):
            return gen
        else:
            vals = [gen]
    return vals

def add(*args, **kwargs):
    data = args[0]
    doc = Tree(data)

    summable = []
    for expr in args[1:]:
        vals = _execute(doc, expr)
        if vals is not None:
            summable += vals

    return sum(summable)

def opath(*args, **kwargs):
    data = args[0]
    doc = Tree(data)

    outputs = []
    for expr in args[1:]:
        vals = _execute(doc, expr)
        if vals is not None:
            outputs += vals

    return outputs

def ascii_unpunc(*args, **kwargs):
    data = args[0]
    doc = Tree(data)

    todo = []
    for expr in args[1:]:
        vals = _execute(doc, expr)
        if vals is not None:
            todo += vals

    return [strings.normalise(s, ascii=True, unpunc=True, lower=True, spacing=True, strip=True, space_replace=False) for s in todo]

def count(*args, **kwargs):
    data = args[0]
    doc = Tree(data)

    list_field = kwargs.get("list_field")
    vals = _execute(doc, list_field)

    if vals is not None:
        return len(vals)
    return 0

def unique_count(*args, **kwargs):
    data = args[0]
    doc = Tree(data)

    list_field = kwargs.get("list_field")
    unique_field = kwargs.get("unique_field")

    vals = _execute(doc, list_field)
    if vals is None:
        return 0

    count = 0
    found = []
    for v in vals:
        subdoc = Tree(v)
        uvals = _execute(subdoc, unique_field)
        if uvals is None:
            continue
        unique = True
        for u in uvals:
            if u in found:
                unique = False
                break
        if unique:
            count += 1
        found += uvals

    return count