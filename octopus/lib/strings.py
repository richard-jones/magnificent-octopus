import string
from unidecode import unidecode
from octopus.lib.coerce import to_unicode

def normalise(s, ascii=True, unpunc=True, lower=True, spacing=True, strip=True, space_replace=False):
    if s is None:
        return u""

    if unpunc:
        throwlist = string.punctuation + '\n\t'
        s = u"".join(c for c in s if c not in throwlist)

    if ascii:
        try:
            s = unidecode(s)
        except:
            pass

    if lower:
        s = s.lower()

    if spacing:
        while "  " in s:
            s = s.replace("  ", " ")

    if strip:
        s = s.strip()

    if space_replace:
        s = s.replace(" ", space_replace)

    # convert to unicode for return
    s = to_unicode(s)

    return s