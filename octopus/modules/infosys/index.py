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