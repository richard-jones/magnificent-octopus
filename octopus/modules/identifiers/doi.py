import re

def normalise(doi):

    doi = doi.strip()

    rx = "^((http(s){0,1}:\/\/){0,1}(dx.){0,1}doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\\..+\/.+)"
    result = re.match(rx, doi)
    if result is None:
        raise ValueError(doi + " does not seem to be a valid DOI")

    doi = result.groups()[-1:][0]

    return doi
