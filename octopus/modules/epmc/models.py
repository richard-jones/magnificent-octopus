from octopus.lib import dataobj
from lxml import etree

class JATSException(Exception):
    def __init__(self, message, rawstring, *args, **kwargs):
        super(JATSException, self).__init__(message, *args, **kwargs)
        self.raw = rawstring

class EPMCFullTextException(JATSException):
    """
    Here for backwards compatibility
    """
    pass

class EPMCMetadataException(Exception):
    def __init__(self, message, rawstring, *args, **kwargs):
        super(EPMCMetadataException, self).__init__(message, *args, **kwargs)
        self.raw = rawstring

class EPMCMetadataXML(object):
    def __init__(self, raw=None, xml=None):
        self.raw = None
        self.xml = None
        if raw is not None:
            self.raw = raw
            try:
                self.xml = etree.fromstring(self.raw)
            except:
                raise JATSException("Unable to parse XML", self.raw)
        elif xml is not None:
            self.xml = xml

    def tostring(self):
        if self.raw is not None:
            return self.raw
        elif self.xml is not None:
            return etree.tostring(self.xml)

    @property
    def author_string(self):
        author_string = self.xml.xpath("//authorString")
        if len(author_string) > 0:
            return author_string[0].text
        return None

    @property
    def authors(self):
        """
        <fullName>Cerasoli E</fullName>
        <firstName>Eleonora</firstName>
        <lastName>Cerasoli</lastName>
        <initials>E</initials>
        <affiliation>Biotechnology Department, National Physical Laboratory Teddington, UK.</affiliation>
        """
        author_elements = self.xml.xpath("//authorList/author")
        obs = []
        for ael in author_elements:
            ao = {}

            fn = ael.find("fullName")
            if fn is not None:
                ao["fullName"] = fn.text

            first = ael.find("firstName")
            if first is not None:
                ao["firstName"] = first.text

            last = ael.find("lastName")
            if last is not None:
                ao["lastName"] = last.text

            inits = ael.find("initials")
            if inits is not None:
                ao["initials"] = inits.text

            aff = ael.find("affiliation")
            if aff is not None:
                ao["affiliation"] = aff.text

            if len(ao.keys()) > 0:
                obs.append(ao)

        return obs

    @property
    def grants(self):
        grant_elements = self.xml.xpath("//grantsList/grant")
        obs = []
        for ael in grant_elements:
            go = {}

            gid = ael.find("grantId")
            if gid is not None:
                go["grantId"] = gid.text

            ag = ael.find("agency")
            if ag is not None:
                go["agency"] = ag.text

            if len(go.keys()) > 0:
                obs.append(go)

        return obs

    @property
    def mesh_descriptors(self):
        mesh_elements = self.xml.xpath("//meshHeadingList/meshHeading/descriptorName")
        return [e.text for e in mesh_elements]



class EPMCMetadata(dataobj.DataObj):
    def __init__(self, raw):
        super(EPMCMetadata, self).__init__(raw)

    @property
    def pmcid(self):
        return self._get_single("pmcid", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def pmid(self):
        return self._get_single("pmid", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def doi(self):
        return self._get_single("doi", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def in_epmc(self):
        return self._get_single("inEPMC", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def is_oa(self):
        return self._get_single("isOpenAccess", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def issn(self):
        return self._get_single("journalInfo.journal.issn", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def journal(self):
        return self._get_single("journalInfo.journal.title", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def essn(self):
        return self._get_single("journalInfo.journal.essn", self._utf8_unicode(), allow_coerce_failure=False)

    @property
    def title(self):
        return self._get_single("title", self._utf8_unicode(), allow_coerce_failure=False)

class JATS(object):
    def __init__(self, raw=None, xml=None):
        self.raw = None
        self.xml = None
        if raw is not None:
            self.raw = raw
            try:
                self.xml = etree.fromstring(self.raw)
            except:
                raise JATSException("Unable to parse XML", self.raw)
        elif xml is not None:
            self.xml = xml

    @property
    def title(self):
        title_elements = self.xml.xpath("//title-group/article-title")
        if len(title_elements) > 0:
            return title_elements[0].text
        return None

    @property
    def is_aam(self):
        manuscripts = self.xml.xpath("//article-id[@pub-id-type='manuscript']")
        return len(manuscripts) > 0

    def get_licence_details(self):
        # get the licence type
        l = self.xml.xpath("//license")
        if len(l) > 0:
            l = l[0]
        else:
            return None, None, None
        type = l.get("license-type")
        url = l.get("{http://www.w3.org/1999/xlink}href")

        # get the paragraph(s) describing the licence
        para = self.xml.xpath("//license/license-p")
        out = ""
        for p in para:
            out += etree.tostring(p)

        return type, url, out

    @property
    def copyright_statement(self):
        cs = self.xml.xpath("//copyright-statement")
        if len(cs) > 0:
            return cs[0].text
        return None

    @property
    def categories(self):
        cs = self.xml.xpath("//article-categories/subj-group/subject")
        return [c.text for c in cs]

    @property
    def contribs(self):
        cs = self.xml.xpath("//contrib-group/contrib")
        obs = []

        for c in cs:
            con = {}

            # first see if there is a name we can pull out
            name = c.find("name")
            if name is not None:
                sn = name.find("surname")
                if sn is not None:
                    con["surname"] = sn.text

                gn = name.find("given-names")
                if gn is not None:
                    con["given-names"] = gn.text

            # see if there's an email address
            email = c.find("email")
            if email is not None:
                con["email"] = email.text

            # now do the affiliations (by value and by (x)reference)
            affs = []

            aff = c.find("aff")
            if aff is not None:
                contents = aff.xpath("string()")
                norm = " ".join(contents.split())
                affs.append(norm)

            xrefs = c.findall("xref")
            for x in xrefs:
                if x.get("ref-type") == "aff":
                    affid = x.get("rid")
                    xp = "//contrib-group/aff[@id='" + affid + "']"
                    aff_elements = self.xml.xpath(xp)
                    for ae in aff_elements:
                        contents = ae.xpath("string()")
                        norm = " ".join(contents.split())
                        affs.append(norm)

            if len(affs) > 0:
                con["affiliations"] = affs

            if len(con.keys()) > 0:
                obs.append(con)

        return obs

    @property
    def emails(self):
        emails = self.xml.xpath("//email")
        return [e.text for e in emails]

    @property
    def keywords(self):
        kws = self.xml.xpath("//kwd-group/kwd")
        return [k.text for k in kws]

    def tostring(self):
        if self.raw is not None:
            return self.raw
        elif self.xml is not None:
            return etree.tostring(self.xml)