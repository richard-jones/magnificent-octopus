import os, json

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'country-codes.json'), 'rb') as f:
    RAW = json.loads(f.read())

class Locality(object):
    def __init__(self, raw=None):
        self._raw = raw if raw is not None else RAW

        self._currency_codes = []
        self._currency_name2code = {}

    def currency_codes(self):
        self._load_currencies()
        return self._currency_codes

    def currency_code_for(self, val):
        self._load_currencies()
        comp = val.lower()
        for k,v in self._currency_name2code.iteritems():
            if k == comp:
                return v
        return None

    def _load_currencies(self):
        if len(self._currency_codes) == 0:
            for code, country_info in self._raw.iteritems():
                if 'currency_alphabetic_code' in country_info and 'currency_name' in country_info:
                    if country_info['currency_alphabetic_code'] not in self._currency_codes:
                        self._currency_name2code[country_info['currency_name']] = country_info['currency_alphabetic_code']
                        self._currency_name2code[country_info['currency_name'].lower()] = country_info['currency_alphabetic_code']
                        self._currency_name2code[country_info['currency_alphabetic_code'].lower()] = country_info['currency_alphabetic_code']
                        self._currency_codes.append(country_info['currency_alphabetic_code'])