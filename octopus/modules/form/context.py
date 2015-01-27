from flask import render_template
from octopus.modules.form import helper
from copy import deepcopy

class FormContextException(Exception):
    pass

class FormContext(object):
    def __init__(self, form_data=None, source=None):
        # initialise our core properties
        self._source = source
        self._target = None
        self._form_data = form_data
        self._form = None
        self._renderer = None
        self._template = None
        self._alert = []

        # initialise the renderer (falling back to a default if necessary)
        self.make_renderer()
        if self.renderer is None:
            self.renderer = Renderer()

        # specify the jinja template that will wrap the renderer
        self.set_template()

        # now create our form instance, with the form_data (if there is any)
        if form_data is not None:
            self.data2form()

        # if there isn't any form data, then we should create the form properties from source instead
        elif source is not None:
            self.source2form()

        # if there is no source, then a blank form object
        else:
            self.blank_form()

    ############################################################
    # getters and setters on the main FormContext properties
    ############################################################

    @property
    def form(self):
        return self._form

    @form.setter
    def form(self, val):
        self._form = val

    @property
    def source(self):
        return self._source

    @property
    def form_data(self):
        return self._form_data

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, val):
        self._target = val

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, val):
        self._renderer = val

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        self._template = val

    @property
    def alert(self):
        return self._alert

    def add_alert(self, val):
        self._alert.append(val)

    ############################################################
    # Lifecycle functions that subclasses should implement
    ############################################################

    def make_renderer(self):
        """
        This will be called during init, and must populate the self.render property
        """
        pass

    def set_template(self):
        """
        This will be called during init, and must populate the self.template property with the path to the jinja template
        """
        pass

    def pre_validate(self):
        """
        This will be run before validation against the form is run.
        Use it to patch the form with any relevant data, such as fields which were disabled
        """
        pass

    def blank_form(self):
        """
        This will be called during init, and must populate the self.form property with an instance of the form in this
        context, based on no originating source or form data
        """
        pass

    def data2form(self):
        """
        This will be called during init, and must convert the form_data into an instance of the form in this context,
        and write to self.form
        """
        pass

    def source2form(self):
        """
        This will be called during init, and must convert the source object into an instance of the form in this
        context, and write to self.form
        """
        pass

    def form2target(self):
        """
        Convert the form object into a the target system object, and write to self.target
        """
        pass

    def patch_target(self):
        """
        Patch the target with data from the source.  This will be run by the finalise method (unless you override it)
        """
        pass

    def finalise(self):
        """
        Finish up with the FormContext.  Carry out any final workflow tasks, etc.
        """
        self.form2target()
        self.patch_target()

    ############################################################
    # Functions which can be called directly, but may be overridden if desired
    ############################################################

    def validate(self):
        self.pre_validate()
        f = self.form
        valid = False
        if f is not None:
            valid = f.validate()

        # if this isn't a valid form, record the fields that have errors
        # with the renderer for use later
        if not valid:
            error_fields = []
            for field in self.form:
                if field.errors:
                    error_fields.append(field.short_name)
            if self.renderer is not None:
                self.renderer.set_error_fields(error_fields)

        return valid

    @property
    def errors(self):
        f = self.form
        if f is not None:
            return f.errors
        return False

    def render_template(self, template=None, **kwargs):
        if template is not None:
            return render_template(template, form_context=self, **kwargs)
        else:
            return render_template(self.template, form_context=self, **kwargs)

    def render_field_group(self, field_group_name=None):
        return self.renderer.render_field_group(self, field_group_name)

class Renderer(object):
    def __init__(self):
        """
        self.FIELD_GROUPS = {
            "group_name" : {
                "helper" : "<helper name>",
                "wrappers" : ["<helper wrappers>"],
                "label_width" : n,
                "control_width" : n,
                "fields" : [
                    {
                        "<field name>" : {
                            "first_error" : True|False (if first_error wrapper is used),
                            "container_class" : "<container class name>" (if container wrapper is used),
                            "hidden" : True|False,
                            "attributes" : {<form field attributes>},
                            "fields" : [  (if this is a FormField)
                                {<structure repeats>}
                            ]
                        }
                    }
                ]
            }
        }
        """
        self.FIELD_GROUPS = {}
        self._error_fields = []
        self._disabled_fields = []

    def render_field_group(self, form_context, field_group_name=None):
        if field_group_name is None:
            return self._render_all(form_context)

        # get the group definition
        group_def = self.FIELD_GROUPS.get(field_group_name)
        if group_def is None:
            return ""

        # get the form helper
        fh = helper.FormHelperFactory.get(group_def.get("helper"), group_def.get("wrappers"))
        label_width = group_def.get("label_width")
        control_width = group_def.get("control_width")

        # build the frag
        frag = ""
        for entry in group_def.get("fields", []):
            field_name = entry.keys()[0]
            config = entry.get(field_name)
            if "label_width" not in config:
                config["label_width"] = label_width
            if "control_width" not in config:
                config["control_width"] = control_width

            # config = self._rewrite_extra_fields(form_context, config)
            field = form_context.form[field_name]

            if field_name in self.disabled_fields:
                config = deepcopy(config)
                if "attributes" not in config:
                    config["attributes"] = {}
                config["attributes"]["disabled"] = "disabled"

            frag += fh.render_field(field, **config)

        return frag

    @property
    def error_fields(self):
        return self._error_fields

    def set_error_fields(self, fields):
        self._error_fields = fields

    @property
    def disabled_fields(self):
        return self._disabled_fields

    def set_disabled_fields(self, fields):
        self._disabled_fields = fields

    def _rewrite_extra_fields(self, form_context, config):
        if "extra_input_fields" in config:
            config = deepcopy(config)
            for opt, field_ref in config.get("extra_input_fields").iteritems():
                extra_field = form_context.form[field_ref]
                config["extra_input_fields"][opt] = extra_field
        return config

    def _render_all(self, form_context):
        frag = ""
        for field in form_context.form:
            frag += self.fh.render_field(form_context, field.short_name)
        return frag

    def find_field(self, field, field_group):
        for index, item in enumerate(self.FIELD_GROUPS[field_group]):
            if field in item:
                return index

    def insert_field_after(self, field_to_insert, after_this_field, field_group):
        self.FIELD_GROUPS[field_group].insert(
            self.find_field(after_this_field, field_group) + 1,
            field_to_insert
        )