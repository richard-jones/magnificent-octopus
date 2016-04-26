from octopus.core import app

from flask import flash, redirect, url_for, request
from flask.ext.login import current_user

def restrict_to_role(role):
    if current_user.is_anonymous():
        flash('You are trying to access a protected area. Please log in first.', 'error')
        return redirect(url_for('account.login', next=request.url))

    if not current_user.has_role(role):
        flash('You do not have permission to access that area of the site.', 'error')
        return redirect(url_for(app.config.get("ACCOUNT_RESTRICTED_AREA_REDIRECT_ROUTE")))