# Accounts Module

This module provides out-of-the-box user accounts for an application:

* Registration and Login features
* Forgotten password tokens
* User roles
* Administrative interface for user management
* Command line tools for user management

## Set-up/configuration

### Quick Start

To support the most basic account capabilities, set the following in your app config:

    ACCOUNT_ENABLE = True
    SECRET_KEY = "something-secret"

and this in your web.py imports:

from octopus.modules.account.account import blueprint as account
app.register_blueprint(account, url_prefix="/account")

Then when you have created a user (see below), you will be able to go to 

    /account/login
    
and log in to the account you created.

### Full Default Set-up

To fully configure the default account system, you can add the following configurations in your app config:

Whether or not to allow previously-unknown users to register for an account:

    ACCOUNT_ALLOW_REGISTER = False

Whether or not to allow an account with the relevant role (list_users) to list the system's user accounts:

    ACCOUNT_LIST_USERS = True

if user listing is enabled, you need to provide a Query endpoint where the data can be retrieved.  This can be 
done by providing the following Query Route configuration for ElasticSearch.

First, set it up in your web.py file:

    from octopus.modules.es.query import blueprint as query
    app.register_blueprint(query, url_prefix="/account_query")

Then configure the query route in your app config as follows:

    QUERY_ROUTE = {
        "account_query" : {
            "account" : {
                "auth" : True,
                "role" : "list-users",
                "filters" : [
                     "octopus.modules.account.dao.query_filter"
                 ],
                "dao" : "octopus.modules.account.dao.BasicAccountDAO"
            }
        }
    }

Finally, let the front-end javascript know where you are setting the endpoint:

    CLIENTJS_ACCOUNT_LIST_ENDPOINT = "/account_query/account"

When user's log in or log out, they will be redirected.  This configuration tells the account system which routes
to redirect the user to:

    ACCOUNT_LOGIN_REDIRECT_ROUTE = "index"
    ACCOUNT_LOGOUT_REDIRECT_ROUTE = "index"


## Creating a user

To create a user from the command line, you can use the usermod octopus script:

    python magnificent-octopus/octopus/bin/run.py usermod -e email@email.com -p password -r admin
    
