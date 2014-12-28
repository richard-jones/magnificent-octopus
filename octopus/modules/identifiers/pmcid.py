def normalise(pmcid):
    pmcid = pmcid.strip()
    if pmcid.startswith("PMC"):
        return pmcid
    else:
        pmcid = "PMC" + pmcid
        return pmcid