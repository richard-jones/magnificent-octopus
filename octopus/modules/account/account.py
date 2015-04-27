import uuid, json

from flask import Blueprint, request, url_for, flash, redirect, make_response
from flask import render_template, abort
from flask.ext.login import login_user, logout_user, current_user, login_required

from octopus.core import app
from octopus.lib.webapp import ssl_required, request_wants_json, flash_with_url, is_safe_url
from octopus.lib import mail
from octopus.modules.account.factory import AccountFactory
from octopus.modules.account import exceptions

blueprint = Blueprint('account', __name__)

@app.login_manager.user_loader
def load_account_for_login_manager(userid):
    from octopus.modules.account.factory import AccountFactory
    acc = AccountFactory.get_model().pull(userid)
    return acc

def get_redirect_target(form=None):
    form_target = ''
    if form and hasattr(form, 'next') and getattr(form, 'next'):
        form_target = form.next.data

    for target in form_target, request.args.get('next', []):
        if not target:
            continue
        if target == is_safe_url(target):
            return target
    return url_for(app.config.get("ACCOUNT_LOGIN_REDIRECT_ROUTE", "index"))


def _do_login(user):
    return login_user(user, remember=True)

def _do_logout():
    logout_user()

@blueprint.route('/login', methods=['GET', 'POST'])
@ssl_required
def login():
    # current_info = {'next': request.args.get('next', '')}
    fc = AccountFactory.get_login_formcontext(request.form)

    if request.method == 'POST':
        if fc.validate():
            password = fc.form.password.data
            email = fc.form.email.data

            Account = AccountFactory.get_model()
            try:
                user = Account.pull_by_email(email)
            except exceptions.NonUniqueAccountException:
                flash("Permanent Error: unable to log you in with these credentials - please contact an administrator", "error")
                return fc.render_template()

            if user is not None:
                if not user.can_log_in():
                    flash('Invalid credentials', 'error')
                    return fc.render_template()

                if user.check_password(password):
                    inlog = _do_login(user)
                    if not inlog:
                        flash("Problem logging in", "error")
                        return fc.render_template()
                    else:
                        flash('Welcome back.', 'success')
                        return redirect(get_redirect_target(form=fc.form))
                else:
                    flash('Incorrect username/password', 'error')
                    return fc.render_template()
            else:
                flash('Incorrect username/password', 'error')
                return fc.render_template()
        else:
            flash('Invalid credentials', 'error')

    return fc.render_template()

@blueprint.route('/logout')
@ssl_required
def logout():
    _do_logout()
    flash('You are now logged out', 'success')
    return redirect(url_for(app.config.get("ACCOUNT_LOGOUT_REDIRECT_ROUTE", "index")))

@blueprint.route('/<username>', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def username(username):
    Account = AccountFactory.get_model()
    acc = Account.pull(username)
    if acc is None:
        try:
            acc = Account.pull_by_email(username)
        except exceptions.NonUniqueAccountException:
            flash("Permanent Error: these user credentials are invalid - please contact an administrator", "error")
            return redirect(url_for(("logut")))

    if acc is None:
        abort(404)

    # actions on this page are only availble to the actual user, or a user with the edit-users role
    if current_user.id != acc.id or not current_user.has_role(app.config.get("ACCOUNT_EDIT_USERS_ROLE")):
        abort(401)

    # if this is a request for the user page, just render it
    if request.method == "GET":
        fc = AccountFactory.get_user_formcontext(acc)
        return fc.render_template()


    is_delete = request.method == "DELETE" or (request.method == "POST" and request.values.get("submit", False) == "Delete")
    if is_delete:
        # validate the delete
        if not current_user.check_password(request.values.get("password")):
            flash("Incorrect password", "error")
            fc = AccountFactory.get_user_formcontext(acc=acc)
            return fc.render_template()

        # if the password validates, go ahead and do it
        acc.remove()    # Note we don't use the DAO's delete method - this allows the model to decide the delete behaviour
        _do_logout()
        flash('Account {x} deleted'.format(x=username), "success")
        return redirect(url_for(app.config.get("ACCOUNT_LOGOUT_REDIRECT_ROUTE", "index")))

    if request.method == "POST":
        fc = AccountFactory.get_user_formcontext(acc=acc, form_data=request.form)

        # attempt to validate the form
        if not fc.validate():
            flash("There was a problem when submitting the form", "error")
            return fc.render_template()

        # if the form validates, then check the legality of the submission
        try:
            fc.legal()
        except exceptions.AccountException as e:
            flash(e.message, "error")
            return fc.render_template()

        # if we get to here, then update the user record
        fc.finalise()

        # tell the user that everything is good
        flash("Account updated", "success")

        # end with a redirect because some details have changed
        return redirect(url_for("account.username", username=fc.target.email))

@blueprint.route('/forgot', methods=['GET', 'POST'])
@ssl_required
def forgot():
    if request.method == "GET":
        fc = AccountFactory.get_forgot_formcontext()
        return fc.render_template()

    if request.method == 'POST':
        fc = AccountFactory.get_forgot_formcontext(form_data=request.form)

        # attempt to validate the form
        if not fc.validate():
            flash("There was a problem when submitting the form", "error")
            return fc.render_template()

        # call finalise on the context, to trigger the reset process
        try:
            fc.finalise()
        except exceptions.NonUniqueAccountException:
            flash("Permanent Error: cannot reset password for this account - please contact an administrator", "error")
            return fc.render_template()
        except exceptions.AccountNotFoundException:
            flash('Your account email address is not recognised.', 'error')
            return fc.render_template()
        except exceptions.AccountException:
            flash("Unable to reset the password for this account", "error")
            return fc.render_template()

        # if we get to here, reset was successful, so we should redirect the user
        return redirect(url_for(app.config.get("ACCOUNT_FORGOT_REDIRECT_ROUTE", "account.forgot_pending")))

@blueprint.route("/forgot-pending", methods=["GET"])
@ssl_required
def forgot_pending():
    return render_template("account/forgot_pending.html")


@blueprint.route("/reset/<reset_token>", methods=["GET", "POST"])
@ssl_required
def reset(reset_token):
    Account = AccountFactory.get_model()
    acc = Account.get_by_reset_token(reset_token)
    if acc is None:
        abort(404)

    if not acc.can_log_in():
        abort(404)



    if request.method == "GET":
        fc = AccountFactory.get_reset_formcontext(acc)
        return fc.render_template()

    elif request.method == "POST":
        fc = AccountFactory.get_reset_formcontext(acc, request.form)
        if not fc.validate():
            flash("There was a problem with your form", "error")
            return fc.render_template()

        # if the form is good, finalise the user's password change
        fc.finalise()

        # log the user in
        _do_login(acc)
        flash("Password has been reset and you have been logged in", "success")
        return redirect(url_for(app.config.get("ACCOUNT_LOGIN_REDIRECT_ROUTE", "index")))



@blueprint.route('/')
@login_required
@ssl_required
def index():
    if not app.config.get("ACCOUNT_LIST_USERS", False):
        abort(404)
    if not current_user.has_role(app.config.get("ACCOUNT_LIST_USERS_ROLE", "list_users")):
        abort(401)
    return render_template('account/users.html')


@blueprint.route('/register', methods=['GET', 'POST'])
@ssl_required
def register():
    form = RegisterForm(request.form, csrf_enabled=False)

    if request.method == 'POST' and form.validate():
        existing_account = models.Account.pull(form.email.data)
        account = None
        if existing_account is not None:
            if existing_account.is_banned():
                flash('You have been banned from using this service.', "error")
                return render_template('account/register.html', form=form)
            elif existing_account.is_deleted():
                flash('Your old account has been restored. Welcome back!', "success")
                existing_account.set_deleted(False, save=False)
                account = existing_account
                account.clear_password()
            else:
                flash('This account already exists.')
                return redirect(url_for('.forgot'))

        if account is None:
            account = models.Account()

        account.id = form.email.data
        account.set_email(form.email.data)
        account.set_name(form.name.data)

        if form.degree.data:
            account.set_degree(form.degree.data)

        if form.phone.data:
            account.set_phone(form.phone.data)

        if form.graduation.data:
            account.set_graduation(form.graduation.data)

        # automatically set the user role to be "user"
        account.add_role("user")

        activation_token = uuid.uuid4().hex
        account.set_activation_token(activation_token, app.config.get("PASSWORD_ACTIVATE_TIMEOUT", 86400))
        account.save()
        account.refresh()  # refresh the index

        #sending the email with the activation link

        sep = "/"
        if request.url_root.endswith("/"):
            sep = ""
        activation_url = request.url_root + sep + "account/activate/" + activation_token

        to = [account.data['email'], app.config['FEEDBACK_EMAIL']]
        fro = app.config['FEEDBACK_EMAIL']
        subject = app.config.get("SERVICE_NAME", "") + " - new password"
        text = "Welcome to UniBoard, '" + account.email + "'!\n\n"
        text += "Please visit " + activation_url + " to set a password for your account.\n\n"
        text += "Regards, The UniBoard Team"
        try:
            mail.send_mail(to=to, fro=fro, subject=subject, text=text)
            flash('Instructions to set up your password have been sent to you. Please check your emails.', "success")
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for activation is ' + activation_url, "error")
        except Exception as e:
            magic = str(uuid.uuid1())
            #util.flash_with_url(
                #'Hm, sorry - sending the password reset email didn\'t work.' + CONTACT_INSTR + ' It would help us if you also quote this magic number: ' + magic + ' . Thank you!',
                #'error')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is ' + activation_url, "error")
            app.logger.error(magic + "\n" + repr(e))

        return redirect('/account/register')  #TODO should be redirecting somewhere else
    if request.method == 'POST' and not form.validate():
        flash('Please correct the errors', 'error')
    return render_template('account/register.html', form=form)


@blueprint.route("/activate/<activation_token>", methods=["GET", "POST"])
@ssl_required
def activate(activation_token):
    account = models.Account.get_by_activation_token(activation_token)
    if account is None:
        abort(404)
    form = SetPasswordForm()
    if request.method == "GET":
        return render_template("account/activate.html", account=account, form=form)

    elif request.method == "POST":
        # check that the passwords match, and bounce if not
        pw = request.values.get("password")
        conf = request.values.get("confirm_password")
        if pw != conf:
            flash("Passwords do not match - please try again", "error")
            return render_template("account/activate.html", account=account, form=form)

        # update the user's account
        account.set_password(pw)
        account.remove_activation_token()
        account.save()
        flash("Password has been set", "success")

        # log the user in
        _do_login(account)
        return redirect('/')



def _get_user_form(acc, use_form_data=False):
    form = None
    if use_form_data:
        form = RegisterForm(request.form, csrf_enabled=False)
        form.email.data = acc.email
    else:
        form = RegisterForm(csrf_enabled=False)
        form.name.data = acc.name
        form.email.data = acc.email
        form.degree.data = acc.degree
        form.postcode.data = acc.postcode
        form.phone.data = acc.phone
        form.graduation.data = acc.graduation
    return form

def _update_account(account, form):
    account.set_name(form.name.data)

    if form.degree.data:
        account.set_degree(form.degree.data)
    elif form.degree.data == "":
        del account.degree

    if form.phone.data:
        account.set_phone(form.phone.data)
    elif form.phone.data == "":
        del account.phone

    if form.graduation.data:
        account.set_graduation(form.graduation.data)
    elif form.graduation.data == "":
        del account.graduation