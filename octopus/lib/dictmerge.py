from copy import deepcopy
import objectpath
import types

class MergeException(Exception):
    pass

class RulesException(Exception):
    pass

def merge(source, target, rules, validate=False):
    """
    The rules for the merge are structured as follows:

    {
        "copy_if_missing" : ["<element to copy from source if key not present in target>"],
        "override" : ["<element to take from source and overwrite any existing value in target>"],
        "list_append" : {
            "<field name>" : {
                "dedupe" : True|False   # whether to attempt to deduplicate lists as they are appended
                "match" : [     # any one of these match blocks can cause a match, so treat them like an OR statement
                    {
                        "object_selector" : "<objectpath json path selector leading to sub-object or sub-list against which matches will happen.  Optional.>",
                        "must" : ["<list of objectpath json path selectors which must all match.  Applied either from the root of the source/target or from the object(s) selected by object_selector>"]
                    }
                ]
            }
        },
        "merge" : {
            "<field name>" : { <merge rules following the same pattern as above, recursively> }
        }
    }

    Note that if a field in list_append is set to dedupe, and a match is found, if there is a rule in the "merge" section, it will be used
    to merge each matching element in the list.

    Rules are applied in an order of precedence:

    1. copy_if_missing
    2. override
    3. list_append
    4. merge

    All fields will be processed exactly once, by the first rule in that order to specify the field.  If action is taken, then the field will be considered "done",
    and if it is specified by a later rule, it will not be acted upon.

    This means that copy_if_missing and override should be considered mutually exclusive - only one of them should specify the field.  If you specify the field in copy_if_missing
    and in override, the override directive will always succeed.

    :param source:
    :param target:
    :param rules:
    :return:
    """

    if not isinstance(source, dict):
        raise MergeException("Provided source is not a dict")
    if not isinstance(target, dict):
        raise MergeException("Provided target is not a dict")

    if validate:
        validate_rules(rules)

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
            done.append(k)                  # we only record this as done if we actually did something, because later rules may wish to revisit (e.g. to merge lists)
        if k not in source and k not in done:
            done.append(k)                  # record it as done for performance purposes, if it isn't in the source data in the first place

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
        if field not in source:
            continue

        if field not in target:
            target[field] = []
        dedupe = instructions.get("dedupe", False)
        if not dedupe:
            target[field] += deepcopy(source[field])
            done.append(field)
            continue

        match = instructions.get("match")
        if match is None:
            # use a standard equivalency match
            found = False
            for v in source[field]:
                if v not in target[field]:
                    target[field].append(deepcopy(v))
                    found = True
            if found:
                done.append(field)
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
                done.append(field)
                continue
            else:
                target[field].append(deepcopy(v))
                done.append(field)


def _merge(source, target, rules, done):
    merges = rules.get("merge", {})
    for field, subrules in merges.iteritems():
        if field in done:
            continue

        merge_source = source.get(field)
        merge_target = target.get(field)

        if merge_source is None and merge_target is None:
            continue
        elif merge_source is None and merge_target is not None:
            continue
        elif merge_source is not None and merge_target is None:
            target[field] = deepcopy(merge_source)
            done.append(field)
        elif merge_source is not None and merge_target is not None:
            merged = merge(merge_source, merge_target, subrules)
            target[field] = merged
            done.append(field)

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


def validate_rules(rules, context=u"root"):
    """
    The rules for the merge are structured as follows:

    {
        "copy_if_missing" : ["<element to copy from source if key not present in target>"],
        "override" : ["<element to take from source and overwrite any existing value in target>"],
        "list_append" : {
            "<field name>" : {
                "dedupe" : True|False   # whether to attempt to deduplicate lists as they are appended
                "match" : [     # any one of these match blocks can cause a match, so treat them like an OR statement
                    {
                        "object_selector" : "<objectpath json path selector leading to sub-object or sub-list against which matches will happen.  Optional.>",
                        "must" : ["<list of objectpath json path selectors which must all match.  Applied either from the root of the source/target or from the object(s) selected by object_selector>"]
                    }
                ]
            }
        },
        "merge" : {
            "<field name>" : { <merge rules following the same pattern as above, recursively> }
        }
    }
    :param rules:
    :return:
    """
    if not isinstance(rules, dict):
        raise RulesException(u"The rules you supplied at {x} were not a dict".format(x=context))

    # first check we've got only the keys we're supposed to have
    keys = rules.keys()
    for k in keys:
        if k not in ["copy_if_missing", "override", "list_append", "merge"]:
            raise RulesException(u"Found {x} but expected one of 'copy_if_missing', 'override', 'list_append', 'merge at {y}'".format(x=k, y=context))

    # now check the specific fields to make sure they are the shape they're supposed to be
    cim = rules.get("copy_if_missing")
    if cim is not None:
        if not isinstance(cim, list):
            raise RulesException(u"copy_if_missing at {x} should be a list".format(x=context))
        for i in range(len(cim)):
            field = cim[i]
            if not isinstance(field, basestring):
                nc = context + u".copy_if_missing[{x}]".format(x=i)
                raise RulesException(u"value at {x} should be a string".format(x=nc))

    over = rules.get("override")
    if over is not None:
        if not isinstance(over, list):
            raise RulesException(u"override at {x} should be a list".format(x=context))
        for i in range(len(over)):
            field = over[i]
            if not isinstance(field, basestring):
                nc = context + u".override[{x}]".format(x=i)
                raise RulesException(u"value at {x} should be a string".format(x=nc))

    la = rules.get("list_append")
    if la is not None:
        if not isinstance(la, dict):
            raise RulesException(u"The list_append directive you supplied at {x} was not a dict".format(x=context))
        for field, instructions in la.iteritems():
            if not isinstance(field, basestring):
                raise RulesException(u"keys for list_append directive at {x} must be strings".format(x=context))
            if not isinstance(instructions, dict):
                raise RulesException(u"values for list_append directive at {x} must be dicts".format(x=context))

            nc = context + ".list_append." + field

            keys = instructions.keys()
            for k in keys:
                if k not in ["dedupe", "match"]:
                    raise RulesException(u"Found {x} but expected one of 'dedupe', 'match' at {y}'".format(x=k, y=nc))

            if "dedupe" in instructions:
                if instructions.get("dedupe") not in [True, False]:
                    raise RulesException(u"Found {x} but expected True/False at {y}'".format(x=instructions.get("dedupe"), y=nc))

            if "match" in instructions:
                matches = instructions.get("match")
                if not isinstance(matches, list):
                    raise RulesException(u"The match directive you supplied at {x} was not a list".format(x=nc))
                for i in range(len(matches)):
                    match = matches[i]
                    if not isinstance(match, dict):
                        raise RulesException(u"values for match directive at {x} must be dicts".format(x=nc))
                    keys = match.keys()
                    for k in keys:
                        if k not in ["object_selector", "must"]:
                            raise RulesException(u"Found {x} but expected one of 'object_selector', 'must' at {y}'".format(x=k, y=nc))

                    if "object_selector" in match:
                        if not isinstance(match.get("object_selector"), basestring):
                            raise RulesException(u"value for object_selector directive at {x} must be a string".format(x=nc + ".match[" + str(i) + "]"))
                        if not match.get("object_selector").startswith("$"):
                            raise RulesException(u"value for object_selector directive at {x} must start with '$' - your objectpath selector is wrong".format(x=nc + ".match[" + str(i) + "]"))

                    if "must" in match:
                        if not isinstance(match.get("must"), list):
                            raise RulesException(u"value for must directive at {x} must be a list".format(x=nc + ".match[" + str(i) + "]"))
                        for must in match.get("must"):
                            if not isinstance(must, basestring):
                                raise RulesException(u"values in must directive at {x} must be strings".format(x=nc + ".match[" + str(i) + "]"))
                            if not must.startswith("$"):
                                raise RulesException(u"values for must directive at {x} must start with '$' - your objectpath selector is wrong".format(x=nc + ".match[" + str(i) + "]"))

    merge = rules.get("merge")
    if merge is not None:
        if not isinstance(merge, dict):
            raise RulesException(u"The merge directive you supplied at {x} was not a dict".format(x=context))

        for field, instructions in merge.iteritems():
            if not isinstance(field, basestring):
                raise RulesException(u"keys for merge directive at {x} must be strings".format(x=context))
            if not isinstance(instructions, dict):
                raise RulesException(u"values for merge directive at {x} must be dicts".format(x=context))

            nc = context + ".merge." + field
            validate_rules(instructions, nc)