from octopus.modules.es import dao
from datetime import datetime

class BasicAccountDAO(dao.ESDAO):
    __type__ = 'account'

    @classmethod
    def pull_by_email(cls, email):
        res = cls.query(q='email:"' + email + '"')
        if res.get('hits', {}).get('total', 0) == 1:
            return cls(res['hits']['hits'][0]['_source'])
        else:
            return None

    @classmethod
    def get_by_reset_token(cls, reset_token, not_expired=True):
        res = cls.query(q='reset_token.exact:"' + reset_token + '"')
        obs = [hit.get("_source") for hit in res.get("hits", {}).get("hits", [])]
        if len(obs) == 0 or len(obs) > 1:
            return None
        expires = obs[0].get("reset_expires")
        if expires is None:
            return None
        if not_expired:
            try:
                ed = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%SZ")
                if ed < datetime.now():
                    return None
            except:
                return None
        return cls(obs[0])

    @classmethod
    def get_by_activation_token(cls, activation_token, not_expired=True):
        res = cls.query(q='activation_token.exact:"' + activation_token + '"')
        obs = [hit.get("_source") for hit in res.get("hits", {}).get("hits", [])]
        if len(obs) == 0 or len(obs) > 1:
            return None
        expires = obs[0].get("activation_expires")
        if expires is None:
            return None
        if not_expired:
            try:
                ed = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%SZ")
                if ed < datetime.now():
                    return None
            except:
                return None
        return cls(obs[0])
