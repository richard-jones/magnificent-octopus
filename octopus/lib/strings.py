import string
from unidecode import unidecode

def normalise(s, ascii=True, unpunc=True, lower=True, spacing=True, strip=True):
    if unpunc:
        throwlist = string.punctuation + '\n\t'
        s = "".join(c for c in s if c not in throwlist)

    if ascii:
        try:
            s = unidecode(s)
        except:
            pass

    if lower:
        s = s.lower()

    if spacing:
        while "  " in s:
            s.replace("  ", " ")

    if strip:
        s = s.strip()

    return s