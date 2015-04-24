class AccountException(Exception):
    pass

class EmailInUseException(AccountException):
    pass

class IncorrectPasswordException(AccountException):
    pass

class NonUniqueAccountException(AccountException):
    pass
