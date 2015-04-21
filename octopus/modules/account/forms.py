from wtforms import Form, validators
from wtforms.fields import StringField, HiddenField, PasswordField
# from octopus.modules.form.validate import
from octopus.modules.form.context import FormContext, Renderer
from octopus.modules.account.factory import AccountFactory

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
        return data

    @classmethod
    def form2obj(cls, form, acc=None):
        if acc is None:
            klazz = AccountFactory.get_model()
            acc = klazz()
        else:
            acc = acc.clone()

        if form.email.data:
            acc.email = form.data.email

        return acc

class BasicUserForm(Form):
    email = StringField("Email", [validators.DataRequired(), validators.Email()])

class BasicUserFormContext(FormContext):
    def set_template(self):
        self.template = "account/view.html"

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
        self.target.save()


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
                    }
                ]
            }
        }


"""
class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if self.next.data == is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


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

class SetPasswordForm(Form):
    old_password = PasswordField("Current Password", [validators.Required()])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Repeat Password', [validators.Required()])

"""