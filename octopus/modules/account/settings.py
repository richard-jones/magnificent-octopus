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
ACCOUNT_LOGIN_FORM_CONTEXT = "octopus.modules.account.forms.LoginFormContext"
ACCOUNT_USER_FORM_CONTEXT = "octopus.modules.account.forms.BasicUserFormContext"
ACCOUNT_FORGOT_FORM_CONTEXT = "octopus.modules.account.forms.ForgotFormContext"
ACCOUNT_RESET_FORM_CONTEXT = "octopus.modules.account.forms.ResetFormContext"

# where to direct the user after login if they haven't already got a page in their "next" location
ACCOUNT_LOGIN_REDIRECT_ROUTE = "index"

# URL routing (suitable for passing to url_for) to redirect the user to on logout
ACCOUNT_LOGOUT_REDIRECT_ROUTE = "index"

# where to direct the user once they have submitted a forgotten password request
ACCOUNT_FORGOT_REDIRECT_ROUTE = "account.forgot_pending"

# amount of time a reset token is valid for (86400 is 24 hours)
ACCOUNT_RESET_TIMEOUT = 86400
ACCOUNT_ACTIVATE_TIMEOUT = ACCOUNT_RESET_TIMEOUT * 14

ACCOUNT_RESET_EMAIL_SUBJECT = "Password reset"
