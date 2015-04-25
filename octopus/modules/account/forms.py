from wtforms import Form, validators
from wtforms.fields import StringField, HiddenField, PasswordField
# from octopus.modules.form.validate import
from octopus.modules.form.context import FormContext, Renderer
from octopus.modules.account.factory import AccountFactory
from octopus.modules.account import exceptions
from flask.ext.login import current_user
from flask import url_for, request
from octopus.core import app
from octopus.lib import mail

#####################################################################
## Login
#####################################################################

class LoginForm(Form):
    next = HiddenField()
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class LoginFormContext(FormContext):
    def set_template(self):
        self.template = "account/login.html"

    def make_renderer(self):
        self.renderer = LoginFormRenderer()

    def blank_form(self):
        self.form = LoginForm(csrf_enabled=False)

    def data2form(self):
        self.form = LoginForm(formdata=self.form_data, csrf_enabled=False)

    def finalise(self):
        super(LoginFormContext, self).finalise()

class LoginFormRenderer(Renderer):
    def __init__(self):
        super(LoginFormRenderer, self).__init__()

        self.FIELD_GROUPS = {
            "login" : {
                "helper" : "bs3_horizontal",
                "wrappers" : ["first_error", "container"],
                "label_width" : 4,
                "control_width" : 8,
                "fields" : [
                    {
                        "next" : {
                            "attributes" : {}
                        }
                    },
                    {
                        "email" : {
                            "attributes" : {}
                        }
                    },
                    {
                        "password" : {
                            "attributes" : {}
                        }
                    }
                ]
            }
        }

###########################################################

class BasicUserFormXwalk(object):
    @classmethod
    def obj2form(cls, acc):
        data = {}
        data["email"] = acc.email
        # Note that we don't crosswalk the password, as this is meaningless
        return data

    @classmethod
    def form2obj(cls, form, acc=None):
        if acc is None:
            klazz = AccountFactory.get_model()
            acc = klazz()
        else:
            acc = acc.clone()

        # update the email address
        if form.email.data:
            acc.email = form.email.data

        # if a new password has been provided, update it
        if form.new_password.data:
            acc.set_password(form.new_password.data)

        return acc

class BasicUserForm(Form):
    email = StringField("Email", [validators.DataRequired(), validators.Email()])

    new_password = PasswordField('New Password', [
        validators.Optional(),
        validators.EqualTo('confirm_new_password', message='Passwords must match')
    ])
    confirm_new_password = PasswordField('Repeat Password', [validators.Optional()])

    password = PasswordField("Current Password", [validators.DataRequired()])

class BasicUserFormContext(FormContext):
    def set_template(self):
        self.template = "account/user.html"

    def make_renderer(self):
        self.renderer = BasicUserFormRenderer()

    def blank_form(self):
        self.form = BasicUserForm()

    def data2form(self):
        self.form = BasicUserForm(formdata=self.form_data)

    def source2form(self):
        data = BasicUserFormXwalk.obj2form(self.source)
        self.form = BasicUserForm(data=data)

    def form2target(self):
        self.target = BasicUserFormXwalk.form2obj(self.form, self.source)

    def finalise(self):
        super(BasicUserFormContext, self).finalise()
        self.target.save(blocking=True)

    def render_template(self, template=None, **kwargs):
        return super(BasicUserFormContext, self).render_template(template=template, account=self.source, **kwargs)

    #####################################################
    ## user form extension to context

    def legal(self):
        # check the password and that the email is not already in use
        if not self._check_password():
            raise exceptions.IncorrectPasswordException("The password you provided was incorrect")

        if not self._check_email():
            raise exceptions.EmailInUseException("The email address you provided is in use by another user")

        return True

    def _check_password(self):
        # we check the password of the logged in user, not the account (this allows for admins to set user passwords)
        return current_user.check_password(self.form.password.data)

    def _check_email(self):
        suggested = self.form.email.data
        provided = self.source.email

        # if they have not changed their email, no need to look any further
        if suggested == provided:
            return True

        # otherwise we need to see if there's an email of this type already
        try:
            existing = AccountFactory.get_model().pull_by_email(suggested)
            return existing is None
        except exceptions.NonUniqueAccountException:
            return False

class BasicUserFormRenderer(Renderer):
    def __init__(self):
        super(BasicUserFormRenderer, self).__init__()

        self.FIELD_GROUPS = {
            "details" : {
                "helper" : "bs3_horizontal",
                "wrappers" : ["first_error", "container"],
                "label_width" : 4,
                "control_width" : 8,
                "fields" : [
                    {
                        "email" : {
                            "attributes" : {}
                        }
                    },
                    {
                        "new_password" : {
                            "attributes" : {}
                        }
                    },
                    {
                        "confirm_new_password" : {
                            "attributes" : {}
                        }
                    },
                    {
                        "password" : {
                            "attributes" : {}
                        }
                    }
                ]
            }
        }

###################################################

class ForgotForm(Form):
    email = StringField("Email", [validators.DataRequired(), validators.Email()])

class ForgotFormContext(FormContext):
    def set_template(self):
        self.template = "account/forgot.html"

    def make_renderer(self):
        self.renderer = ForgotFormRenderer()

    def blank_form(self):
        self.form = ForgotForm()

    def data2form(self):
        self.form = ForgotForm(formdata=self.form_data)

    def finalise(self):
        super(ForgotFormContext, self).finalise()

        Account = AccountFactory.get_model()
        acc = Account.pull_by_email(self.form.email.data)
        if acc is None:
            raise exceptions.AccountNotFoundException("There is no user account with that email address")

        acc.activate_reset_mode()
        acc.save()

        self._send_reset_email(acc)

    def _send_reset_email(self, acc):
        base = request.url_root
        if base.endswith("/"):
            base = base[:-1]
        reset_url = base + url_for("account.reset", reset_token=acc.reset_token)

        to = [acc.email]
        fro = app.config.get('MAIL_FROM_ADDRESS')
        subject = app.config.get("ACCOUNT_RESET_EMAIL_SUBJECT", "(no subject)")

        try:
            mail.send_mail(to=to, fro=fro, subject=subject, template_name="account/emails/password_reset.txt", reset_url=reset_url, account=acc)
        except Exception as e:
            raise exceptions.EmailFailedException("Unable to send email to the address provided", e)

class ForgotFormRenderer(Renderer):
    def __init__(self):
        super(ForgotFormRenderer, self).__init__()

        self.FIELD_GROUPS = {
            "email" : {
                "helper" : "bs3_horizontal",
                "wrappers" : ["first_error", "container"],
                "label_width" : 4,
                "control_width" : 8,
                "fields" : [
                    {
                        "email" : {
                            "attributes" : {}
                        }
                    }
                ]
            }
        }

######################################################

"""

class RegisterForm(Form):
    name = TextField('Full name', [validators.Required()])
    email = TextField('Email Address',
                    [
                        validators.Required(),
                        validators.Length(min=3, max=35),
                        validators.Email(message='Must be a valid email address')
                    ],
                    description="You must use your institutional email here")
    degree = TextField('Course')
    postcode = TextField('Postcode of term-time residence',
                         description='We will use this postcode to obtain the approximate location of your term-time residence, to give you information about items for sale that are close to you.',)
    phone = TextField('Phone number')
    graduation = TextField('Graduation Year')

"""