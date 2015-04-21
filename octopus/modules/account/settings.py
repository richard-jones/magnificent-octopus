# If you are going to use the account module, you need to add the DAO to the ES
# mappings with
#
#ELASTIC_SEARCH_MAPPINGS = [
#  octopus.modules.account.dao.BasicAccountDAO
#]

# make this something secret in your overriding local.cfg
SECRET_KEY = "default-key"

# role which denotes a super user
ACCOUNT_SUPER_USER_ROLE = "admin"

# Model object (must extend from BasicAccount) for managing user accounts
ACCOUNT_MODEL = "octopus.modules.account.models.BasicAccount"

# whether the UI for listing users should be available, and to which user role
ACCOUNT_LIST_USERS = False
ACCOUNT_LIST_USERS_ROLE = "list_users"

# the user role which allows a user to edit other user accounts
ACCOUNT_EDIT_USERS_ROLE = "edit_users"

# should unregsitered/unauthenticated people be allowed to hit the registration page
ACCOUNT_ALLOW_REGISTER = False

# UI Form Contexts for the various interface aspects
ACCOUNT_USER_FORM_CONTEXT = "octopus.modules.account.forms.BasicUserFormContext"
ACCOUNT_LOGIN_FORM_CONTEXT = "octopus.modules.account.forms.LoginFormContext"


# amount of time a reset token is valid for (86400 is 24 hours)
PASSWORD_RESET_TIMEOUT = 86400
PASSWORD_ACTIVATE_TIMEOUT = PASSWORD_RESET_TIMEOUT * 14
