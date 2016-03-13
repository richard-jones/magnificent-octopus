from copy import deepcopy
import objectpath
import types

def merge(source, target, rules):
    target = deepcopy(target)
    done = []

    _copy_if_missing(source, target, rules, done)
    _override(source, target, rules, done)
    _list_append(source, target, rules, done)
    _merge(source, target, rules, done)

    return target


def _copy_if_missing(source, target, rules, done):
    cim = rules.get("copy_if_missing", [])
    for k in cim:
        if k in source and k not in target and k not in done:
            target[k] = deepcopy(source[k])
            done.append(k)

def _override(source, target, rules, done):
    over = rules.get("override", [])
    for k in over:
        if k in source and k not in done:
            target[k] = deepcopy(source[k])
            done.append(k)

def _list_append(source, target, rules, done):
    la = rules.get("list_append", {})
    for field, instructions in la.iteritems():
        if field in done:
            continue
        else:
            done.append(field)

        if field not in target:
            target[field] = []
        dedupe = instructions.get("dedupe", False)
        if not dedupe:
            target[field] += deepcopy(source[field])
            continue

        match = instructions.get("match")
        if match is None:
            # use a standard equivalency match
            for v in source[field]:
                if v not in target[field]:
                    target[field].append(deepcopy(v))
            continue

        # for each source field, for each criteria, look at each target field to determine if there
        # is a match
        for v in source[field]:
            found = False
            for criteria in match:
                for i in range(len(target[field])):     # use a range, because we need to know the index number
                    tv = target[field][i]
                    if _match(v, tv, criteria):
                        # if we find a match we either continue without doing anything, or merge the records if
                        # there is a merge rule
                        mr = rules.get("merge", {}).get(field)
                        if mr is not None:
                            res = merge(v, tv, mr)
                            target[field][i] = res
                        found = True
                        break
            if found:
                continue
            else:
                target[field].append(deepcopy(v))


def _merge(source, target, rules, done):
    pass

def _execute(tree, expr):
    vals = []
    gen = tree.execute(expr)
    if gen is not None:
        if isinstance(gen, types.GeneratorType):
            vals = [x for x in gen]
        elif isinstance(gen, list):
            vals = gen
        else:
            vals = [gen]
    return vals

def _match(obj1, obj2, criteria):
    os = criteria.get("object_selector")
    must = criteria.get("must")

    # we want to perform the "must" match between 2 lists of objects.  If one object in one list
    # matches one object in the other list, this is a successful match.
    #
    # we need to take obj1 and obj2 as our initial conditions, in case an object_selector is not
    # provided, in which case the match will just be between 2 single element lists containing
    # the original objects
    matchobjs1 = [objectpath.Tree(obj1)]
    matchobjs2 = [objectpath.Tree(obj2)]

    # if an object selector is provided, we can override the above setters with the selected sub objects
    if os is not None:
        tree1 = objectpath.Tree(obj1)
        tree2 = objectpath.Tree(obj2)
        matchobjs1 = [objectpath.Tree(doc) for doc in _execute(tree1, os)]
        matchobjs2 = [objectpath.Tree(doc) for doc in _execute(tree2, os)]

    # now we have a list of 0 or more records in each matchobjs list
    # so iterate over them, looking for matches.
    # The criteria for a match is that all values for each must must all match
    # any two records, one from matchobjs1 and one from matchobjs2, that match mean that
    # there is a match
    for m1 in matchobjs1:
        for m2 in matchobjs2:
            matched = True
            for m in must:
                m1vals = _execute(m1, m)
                m2vals = _execute(m2, m)
                m1vals.sort()
                m2vals.sort()
                if m1vals == m2vals:
                    continue
                else:
                    matched = False
                    break
            if matched:
                return True

    return False
