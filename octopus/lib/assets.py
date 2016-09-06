import json, shutil, os, subprocess
from copy import deepcopy
from random import randint

def build_assets(config, outputs=None):
    # if no outputs are specified, do all of them
    if outputs is None:
        outputs = config.get("outputs", {}).keys()

    # start by constructing the temporary file structure for the build
    tmpdir = config.get("parameters", {}).get("tmp_dir", "tmp")

    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    os.mkdir(tmpdir)

    js_compdir = os.path.join(tmpdir, "js")
    css_compdir = os.path.join(tmpdir, "css")
    os.mkdir(js_compdir)
    os.mkdir(css_compdir)

    for output in outputs:
        outcfg = config.get("outputs", {}).get(output, {})
        idents = outcfg.get("assets", [])
        idents = _sequence(idents, config)
        sources = _resolve_sources(idents, config)
        compiled = []
        if outcfg.get("pipeline") == "js":
            compiled = _uglify(sources, js_compdir, config)
        elif outcfg.get("pipeline") == "css":
            compiled = _minify_css(sources, css_compdir, config)

        path_elements = outcfg.get("out")
        outfile = _pathify(path_elements, config)
        _cat(compiled, outfile)

    if config.get("parameters", {}).get("cleanup", True):
        shutil.rmtree(tmpdir)

def _cat(sources, outfile):
    with open(outfile, 'w') as f:
        for fname in sources:
            with open(fname) as infile:
                f.write(infile.read())
            f.write("\n")

def _minify_css(sources, outdir, config):
    node = config.get("parameters", {}).get("node", "node")
    r_file = config.get("parameters", {}).get("r_file", "r.js")
    outputs = []
    for source in sources:
        fn = os.path.split(source)[-1]
        prefix = _random()
        out = os.path.join(outdir, prefix + "_" + fn)
        outputs.append(out)
        cmd = "{node} {r_file} -o cssIn={source} out={out} baseUrl=.".format(node=node, r_file=r_file, source=source, out=out)
        print cmd
        print subprocess.call(cmd, shell=True)
    return outputs

def _uglify(sources, outdir, config):
    node = config.get("parameters", {}).get("node", "node")
    uglify = config.get("parameters", {}).get("uglify", "uglifyjs")
    outputs = []
    for source in sources:
        fn = os.path.split(source)[-1]
        prefix = _random()
        out = os.path.join(outdir, prefix + "_" + fn)
        outputs.append(out)
        cmd = "{node} {uglify} -o {out} {source}".format(node=node, uglify=uglify, source=source, out=out)
        print cmd
        print subprocess.call(cmd, shell=True)
    return outputs


def _resolve_sources(idents, config):
    sources = []
    for ident in idents:
        path_elements = config.get("assets", {}).get(ident)
        if path_elements is None:
            print "No path element for " + ident
            exit()
        path = _pathify(path_elements, config)
        sources.append(path)
    return sources

def _pathify(path_elements, config):
    base_path = config.get("base_paths", {}).get(path_elements[0])
    if base_path is None:
        print "No base path for " + path_elements[0]
        exit()
    path = os.path.join(base_path, path_elements[1])
    return path

def _sequence(idents, config):
    dependencies = deepcopy(config.get("dependencies", {}))
    sequenced = _sequence_dependencies(dependencies)

    # first, just copy any that don't have dependencies declared
    ordered = []
    for ident in idents:
        if ident not in dependencies.keys():
            ordered.append(ident)

    for a in sequenced:
        if a in idents and a not in ordered:
            ordered.append(a)

    return ordered

def _sequence_dependencies(dependencies):

    # expand the dependencies
    expanded = {}
    for k, v in dependencies.iteritems():
        expanded[k] = v
        for d in v:
            if d not in dependencies.keys():
                expanded[d] = []

    # now sequence the dependencies which don't, themselves, have dependencies
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file for asset compilation")
    args = parser.parse_args()

    if not args.config:
        print "Please specify a config file with the -c option"
        exit()

    with open(args.config) as f:
        obj = json.loads(f.read())

    build_assets(obj)