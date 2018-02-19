import re

def normalise(doi):

    doi = doi.strip()

    rx = "^((https?:\/\/)?(dx\.)?doi.org/|(https?:\/\/)?hdl\.handle\.net\/|doi:|info:doi:)?(?P<id>10\\..+\/.+)"
    result = re.match(rx, doi)
    if result is None:
        raise ValueError(doi + " does not seem to be a valid DOI")

    doi = result.groups()[-1:][0]

    return doi
