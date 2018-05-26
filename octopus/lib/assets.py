"""
Module for compiling javascript and css assets into minified resources with all dependencies satisfied
"""
import json, shutil, os, subprocess, codecs, collections
from copy import deepcopy
from random import randint

def build_assets(config, outputs=None):
    # start by constructing the temporary file structure for the build
    tmpdir = config.get("parameters", {}).get("tmp_dir", "tmp")
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    os.mkdir(tmpdir)

    js_compdir = os.path.join(tmpdir, "js")
    css_compdir = os.path.join(tmpdir, "css")
    os.mkdir(js_compdir)
    os.mkdir(css_compdir)

    # first, assemble the full config from the embedded imports
    imports = config.get("import", {})
    imported = []
    for k, v in imports.iteritems():
        with open(v) as f:
            imp = json.loads(f.read())
        localised = _localise_import(k, os.path.dirname(v), imp)
        imported.append(localised)
        localised_file = os.path.join(tmpdir, k + "_assets.json")
        with open(localised_file, "w") as f:
            f.write(json.dumps(localised, indent=2, sort_keys=True))

    # now merge all the imports with the primary config
    for imp in imported:
        config = _merge_import(config, imp)
    full_file = os.path.join(tmpdir, "full_assets.json")
    with open(full_file, "w") as f:
        f.write(json.dumps(config, indent=2, sort_keys=True))

    # if no outputs are specified, do all of them
    if outputs is None:
        outputs = config.get("outputs", {}).keys()

    # construct each output
    for output in outputs:
        # get a list of the assets that are the target of the build
        outcfg = config.get("outputs", {}).get(output, {})
        asset_idents = outcfg.get("assets", [])

        # bottom out all the dependencies from the list
        all_idents = _expand_dependencies(asset_idents, config)

        # sequence the assets we want to use according to their dependencies
        all_idents = _sequence(all_idents, config)

        # filter the identifiers
        filtered_idents = _filter_idents(all_idents, outcfg, config)

        # resolve the source paths for each asset
        sources = _resolve_sources(filtered_idents, config)

        # apply the appropriate build pipelines to the list of ordered sources
        pipelines = outcfg.get("pipelines", {}).keys()
        for pipeline in pipelines:
            PIPELINES[pipeline](output, sources, outcfg, config)

    if config.get("parameters", {}).get("cleanup", True):
        shutil.rmtree(tmpdir)


def _merge_import(target, source):
    for k, v in source.iteritems():
        if isinstance(v, collections.Mapping):
            target[k] = _merge_import(target.get(k, {}), v)
        else:
            target[k] = v
    return target

def _localise_import(name, path, config):
    config = deepcopy(config)
    if "parameters" in config:
        del config["parameters"]

    new_base_paths = {}
    for k, v in config.get("base_paths", {}).iteritems():
        new_base_paths[name + "_" + k] = os.path.join(path, v)
    config["base_paths"] = new_base_paths

    new_assets = {}
    for k, v in config.get("assets", {}).iteritems():
        new_assets[k] = [name + "_" + v[0], v[1]]
    config["assets"] = new_assets

    if "outputs" in config:
        del config["outputs"]

    return config

def _cat(sources, outfile):
    with open(outfile, 'w') as f:
        for fname in sources:
            with open(fname) as infile:
                f.write(infile.read())
            f.write("\n")


def _filter_idents(idents, outcfg, config):

    if "exclude" in outcfg:
        idents = deepcopy(idents)
        excludes = outcfg.get("exclude", [])
        for exclude in excludes:
            for i in range(len(idents)):
                if idents[i] == exclude:
                    del idents[i]
                    break

    elif "include" in outcfg:
        includes = outcfg.get("include", [])
        to_include = []
        for inc in includes:
            if inc in idents:
                to_include.append(inc)
        idents = to_include

    return idents


def _resolve_sources(idents, config):
    sources = []
    for ident in idents:
        type = "asset"
        path_elements = config.get("assets", {}).get(ident)
        if path_elements is None:
            path_elements = config.get("references", {}).get(ident)
            type = "reference"
        if path_elements is None:
            print "No path element for " + ident
            exit()

        if type == "asset":
            path = _pathify(path_elements, config)
            sources.append(("asset", path))
        elif type == "reference":
            sources.append(("reference", path_elements))
    return sources

def _pathify(path_elements, config):
    base_path = config.get("base_paths", {}).get(path_elements[0])
    if base_path is None:
        print "No base path for " + path_elements[0]
        exit()
    path = os.path.join(base_path, path_elements[1])
    return path


def _expand_dependencies(idents, config):
    dependencies = deepcopy(config.get("dependencies", {}))
    fulldeps = set(deepcopy(idents))

    while True:
        newdeps = set(deepcopy(fulldeps))
        for ident in fulldeps:
            transients = dependencies.get(ident, [])
            for t in transients:
                newdeps.add(t)

        if len(fulldeps) == len(newdeps):
            return list(fulldeps)
        fulldeps = newdeps


def _sequence(idents, config):
    dependencies = deepcopy(config.get("dependencies", {}))
    sequenced = _sequence_dependencies(dependencies)

    # first, just copy any that don't have dependencies declared
    ordered = []
    for ident in idents:
        if ident not in dependencies.keys():
            ordered.append(ident)

    # then get all of the sequenced dependencies in order if they have not already
    # been taken
    for a in sequenced:
        if a in idents and a not in ordered:
            ordered.append(a)

    return ordered

def _sequence_dependencies(dependencies):

    # expand the dependencies, so every dependency has an entry in the list (even if they then declare no additional
    # dependencies
    expanded = {}
    for k, v in dependencies.iteritems():
        expanded[k] = v
        for d in v:
            if d not in dependencies.keys():
                expanded[d] = []

    # now sequence the dependencies which don't, themselves, have dependencies
    #
    # do this by iterating over the expanded list of dependencies, gathering up all those which don't
    # have any dependencies of their own and adding them to the "sequenced" list.  Then remove those items
    # from the expanded list, and remove mentions of them from other dependencies.  This will cause all
    # entries in the list to have their dependency list length tend towards zero, as their dependencies are
    # sequenced.
    sequenced = []

    while len(expanded.keys()) > 0:
        removes = []
        for k, v in expanded.iteritems():
            if len(v) == 0:
                sequenced.append(k)
                removes.append(k)

        remove_map = {}
        for r in removes:
            del expanded[r]
            for k, v in expanded.iteritems():
                if r in v:
                    idx = v.index(r)
                    if k in remove_map:
                        remove_map[k].append(idx)
                    else:
                        remove_map[k] = [idx]
        for k, v in remove_map.iteritems():
            v.sort(reverse=True)
            for idx in v:
                del expanded[k][idx]

    return sequenced

def _random():
    return str(randint(10000, 99999))


def _css_pipeline(name, sources, outcfg, config):
    node = config.get("parameters", {}).get("node", "node")
    r_file = config.get("parameters", {}).get("r_file", "r.js")
    tmpdir = config.get("parameters", {}).get("tmp_dir", "tmp")
    css_compdir = os.path.join(tmpdir, "css")

    outputs = []
    for source in sources:
        if source[0] == "reference":
            continue
        fn = os.path.split(source[1])[-1]
        prefix = name + "_" + _random()
        out = os.path.join(css_compdir, prefix + "_" + fn)
        outputs.append(out)
        cmd = "{node} {r_file} -o cssIn={source} out={out} baseUrl=.".format(node=node, r_file=r_file, source=source[1], out=out)
        print cmd
        print subprocess.call(cmd, shell=True)

    path_elements = outcfg.get("pipelines", {}).get("css-src", {}).get("out")
    outfile = _pathify(path_elements, config)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    _cat(outputs, outfile)


def _css_includes_pipeline(name, sources, outcfg, config):
    substitutions = outcfg.get("pipelines", {}).get("css-includes", {}).get("path_prefix_substitutions", {})
    frag = ""
    for source in sources:
        s = source[1]
        for sub, rep in substitutions.iteritems():
            if s.startswith(sub):
                s = s.replace(sub, rep, 1)
                break
        frag += '<link rel="stylesheet" href="' + s + '">\n'

    path_elements = outcfg.get("pipelines", {}).get("css-includes", {}).get("out")
    outfile = _pathify(path_elements, config)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    with codecs.open(outfile, "wb", "utf-8") as f:
        f.write(frag)

def _js_pipeline(name, sources, outcfg, config):
    node = config.get("parameters", {}).get("node", "node")
    uglify = config.get("parameters", {}).get("uglify", "uglifyjs")
    tmpdir = config.get("parameters", {}).get("tmp_dir", "tmp")
    js_compdir = os.path.join(tmpdir, "js")

    outputs = []
    for source in sources:
        if source[0] == "reference":
            continue
        fn = os.path.split(source[1])[-1]
        prefix = name + "_" + _random()
        out = os.path.join(js_compdir, prefix + "_" + fn)
        outputs.append(out)
        cmd = "{node} {uglify} -o {out} {source}".format(node=node, uglify=uglify, source=source[1], out=out)
        print cmd
        print subprocess.call(cmd, shell=True)

    path_elements = outcfg.get("pipelines", {}).get("js-src", {}).get("out")
    outfile = _pathify(path_elements, config)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    _cat(outputs, outfile)


def _js_includes_pipeline(name, sources, outcfg, config):
    substitutions = outcfg.get("pipelines", {}).get("js-includes", {}).get("path_prefix_substitutions", {})
    frag = ""
    for source in sources:
        s = source[1]
        for sub, rep in substitutions.iteritems():
            if s.startswith(sub):
                s = s.replace(sub, rep, 1)
                break
        frag += '<script type="text/javascript" src="' + s + '"></script>\n'

    path_elements = outcfg.get("pipelines", {}).get("js-includes", {}).get("out")
    outfile = _pathify(path_elements, config)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    with codecs.open(outfile, "wb", "utf-8") as f:
        f.write(frag)

def _concatenate(name, sources, outcfg, config):
    outputs = []
    for source in sources:
        if source[0] == "reference":
            continue
        outputs.append(source[1])

    path_elements = outcfg.get("pipelines", {}).get("cat", {}).get("out")
    outfile = _pathify(path_elements, config)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    _cat(outputs, outfile)


PIPELINES = {
    "js-src" : _js_pipeline,
    "js-includes" : _js_includes_pipeline,
    "css-src" : _css_pipeline,
    "css-includes" : _css_includes_pipeline,
    "cat" : _concatenate
}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file for asset compilation")
    parser.add_argument("-o", "--outputs", help="list of outputs to compile")
    args = parser.parse_args()

    if not args.config:
        print "Please specify a config file with the -c option"
        exit()

    with open(args.config) as f:
        obj = json.loads(f.read())

    outputs = None
    if args.outputs is not None:
        outputs = [o.strip() for o in args.outputs.split(",")]

    build_assets(obj, outputs)