class FormHelperFactory(object):
    @classmethod
    def get(cls, helper_type, wrapper_chain):
        ht = None
        if helper_type == "bs3_horizontal":
            ht =  FormHelperBS3Horizontal()

        inner = ht
        if wrapper_chain is not None:
            for wrapper in reversed(wrapper_chain):
                if wrapper == "first_error":
                    inner = FirstErrorWrapper(inner)
                elif wrapper == "container":
                    inner = ContainerWrapper(inner)

        return inner

class FirstErrorWrapper(object):
    def __init__(self, inner):
        self.inner = inner

    def render_field(self, field, **kwargs):
        first_error = kwargs.pop("first_error", False)

        frag = ""
        if first_error:
            frag += '<a name="first_problem"></a>'

        frag += self.inner.render_field(field, **kwargs)

        return frag

class ContainerWrapper(object):
    def __init__(self, inner):
        self.inner = inner

    def render_field(self, field, **kwargs):
        container_class = kwargs.pop("container_class", "")
        frag = "<div class='" + container_class + "'>"
        frag += self.inner.render_field(field, **kwargs)
        frag += "</div>"
        return frag

class FormHelperBS3Horizontal(object):

    def render_field(self, field, **kwargs):
        # Render a field with the standard horizontal bootstrap form

        # call the correct render function on the field type
        if field.type == "FormField":
            return self._form_field(field, **kwargs)
        elif field.type == "FieldList":
            return self._field_list(field, **kwargs)
        else:
            return self._form_group(field, **kwargs)

    def _form_field(self, field, **kwargs):
        frag = ""

        label_width = kwargs.get("label_width")
        control_width = kwargs.get("control_width")

        for entry in kwargs.get("fields", []):
            field_name = entry.keys()[0]
            config = entry.get(field_name)
            if "label_width" not in config:
                config["label_width"] = label_width
            if "control_width" not in config:
                config["control_width"] = control_width

            # config = self._rewrite_extra_fields(form_context, config)
            subfield = field[field_name]

            frag += self.render_field(subfield, **config)

        return frag

    def _field_list(self, field, **kwargs):
        # for each subfield, do the render
        frag = ""
        for subfield in field:
            frag += self.render_field(subfield, **kwargs)
        return frag

    def _form_group(self, field, **kwargs):
        hidden = kwargs.pop("hidden", False)
        suppress = kwargs.pop("suppress_form_group", False)

        frag = ""
        if not suppress:
            frag += '<div class="form-group'
            if field.errors:
                frag += " error"
            frag += '" id="'
            frag += field.short_name + '-form-group"'
            if hidden:
                frag += ' style="display:none;"'
            frag += ">"
        frag += self._input_field(field, **kwargs)
        if not suppress:
            frag += "</div>"

        return frag

    def _input_field(self, field, **kwargs):
        if field.type == 'CSRFTokenField' and not field.value:
            return ""

        label_width = kwargs.pop("label_width")
        control_width = kwargs.pop("control_width")

        if label_width is None and control_width is None:
            label_width, control_width = 4, 8
        elif label_width is None and control_width is not None:
            label_width = 12 - control_width
        elif label_width is not None and control_width is None:
            control_width = 12 - label_width

        # determine if this is a checkbox
        is_checkbox = False
        if (field.type == "SelectMultipleField"
                and field.option_widget.__class__.__name__ == 'CheckboxInput'
                and field.widget.__class__.__name__ == 'ListWidget'):
            is_checkbox = True

        if field.type == "BooleanField":
            is_checkbox = True

        frag = ""

        # If this is the kind of field that requires a (separate) label, give it one
        # (note that BooleanFields (checkboxes) come with their own label
        if field.type not in ['SubmitField', 'HiddenField', 'CSRFTokenField', "BooleanField"]:
            frag += '<label class="col-sm-' + str(label_width) + ' control-label" for="' + field.short_name + '">'
            frag += field.label.text
            if field.flags.required or field.flags.display_required_star:
                frag += '&nbsp;<span class="required">*</span>'
            frag += "</label>"

        # render the div which will contain the form controls
        classes = []
        if is_checkbox:
            classes.append("checkbox")
        else:
            classes.append("col-sm-" + str(control_width))
            classes.append("controls")

        frag += '<div class="' + " ".join(classes) + '">'

        attributes = kwargs.pop("attributes", {})
        if "class" in attributes:
            attributes["class"] += " form-control"
        else:
            attributes["class"] = "form-control"

        if field.type == "RadioField":
            for subfield in field:
                frag += self._render_radio(subfield, **kwargs)
        elif is_checkbox:
            #frag += '<ul id="' + field.short_name + '">'
            #for subfield in field:
            frag += self._render_checkbox(field, **kwargs)
            #frag += "</ul>"
        else:
            frag += field(**attributes)

        if field.errors:
            frag += '<ul class="errors">'
            for error in field.errors:
                frag += '<li>' + error + '</li>'
            frag += "</ul>"

        if field.description:
            frag += '<p class="help-block">' + field.description + '</p>'

        frag += "</div>"
        return frag

    def _render_radio(self, field, **kwargs):
        frag = '<label class="radio" for="' + field.short_name + '">'
        frag += field(**kwargs)
        frag += '<span class="label-text">' + field.label.text + '</span>'
        frag += "</label>"
        return frag

    def _render_checkbox(self, field, **kwargs):
        frag = "<label>"
        frag += field(**kwargs)
        frag += "&nbsp;" + field.label.text + "&nbsp;&nbsp;"
        frag += '</label>'
        return frag


"""
This is the old form helper which the above classes supersede
class FormHelper(object):

    def _form_group(self, field, container_class=None, hidden=False, render_subfields_horizontal=False, **kwargs):
        frag = '<div class="form-group'
        if field.errors:
            frag += " error"
        if container_class is not None:
            frag += " " + container_class
        frag += '" id="'
        frag += field.short_name + '-container"'
        if hidden:
            frag += ' style="display:none;"'
        frag += ">"
        frag += self._render_field(field, **kwargs)
        frag += "</div>"

        return frag

    def render_field(self, field, **kwargs):
        # FIXME: disabled = form_context.is_disabled(field_name)

        # begin the frag
        frag = ""

        # deal with the first error if it is relevant
        first_error = kwargs.pop("first_error", False)
        if first_error:
            frag += '<a name="first_problem"></a>'

        # call the correct render function on the field type
        if field.type == "FormField":
            frag += self._form_field(field, **kwargs)
        elif field.type == "FieldList":
            frag += self._field_list(field, **kwargs)
        else:
            hidden = kwargs.pop("hidden", False)
            container_class = kwargs.pop("container_class", None)
            frag += self._form_group(field, container_class=container_class, hidden=hidden, **kwargs)

        return frag

    def _form_field(self, field, **kwargs):
        # get the useful kwargs
        hidden = kwargs.pop("hidden", False)
        render_subfields_horizontal = kwargs.pop("render_subfields_horizontal", False)
        container_class = kwargs.pop("container_class", None)

        frag = ""

        # for each subfield, do the render
        for subfield in field:
            if render_subfields_horizontal and not (subfield.type == 'CSRFTokenField' and not subfield.value):
                subfield_width = "3"
                remove = []
                for kwarg, val in kwargs.iteritems():
                    if kwarg == 'subfield_display-' + subfield.short_name:
                        subfield_width = val
                        remove.append(kwarg)
                for rm in remove:
                    del kwargs[rm]
                frag += '<div class="span' + subfield_width + ' nested-field-container">'
                frag += self.render_field(subfield, maximise_width=True, **kwargs)
                frag += "</div>"
            else:
                frag += self.render_field(subfield, **kwargs)

        return frag

    def _field_list(self, field, **kwargs):
        # for each subfield, do the render
        frag = ""
        for subfield in field:
            if subfield.type == "FormField":
                frag += self.render_field(subfield, **kwargs)
            else:
                hidden = kwargs.pop("hidden", False)
                frag += self._form_group(field, hidden=hidden, **kwargs)
        return frag

    def _render_field(self, field, **kwargs):
        # interesting arguments from keywords
        extra_input_fields = kwargs.get("extra_input_fields")
        q_num = kwargs.pop("q_num", None)
        maximise_width = kwargs.pop("maximise_width", False)
        clazz = kwargs.get("class", "")

        if field.type == 'CSRFTokenField' and not field.value:
            return ""

        frag = ""

        # If this is the kind of field that requires a label, give it one
        if field.type not in ['SubmitField', 'HiddenField', 'CSRFTokenField']:
            if q_num is not None:
                frag += '<a class="animated" name="' + q_num + '"></a>'
            frag += '<label class="col-sm-4 control-label" for="' + field.short_name + '">'
            if q_num is not None:
                frag += '<a class="animated orange" href="#' + field.short_name + '-container" title="Link to this question" tabindex="-1">' + q_num + ')</a>&nbsp;'
            frag += field.label.text
            if field.flags.required or field.flags.display_required_star:
                frag += '&nbsp;<span class="red">*</span>'
            frag += "</label>"

        # determine if this is a checkbox
        is_checkbox = False
        if (field.type == "SelectMultipleField"
                and field.option_widget.__class__.__name__ == 'CheckboxInput'
                and field.widget.__class__.__name__ == 'ListWidget'):
            is_checkbox = True

        extra_class = ""
        if is_checkbox:
            extra_class += " checkboxes"

        frag += '<div class="col-sm-8 controls' + extra_class + '">'
        if field.type == "RadioField":
            for subfield in field:
                frag += self._render_radio(subfield, **kwargs)
        elif is_checkbox:
            frag += '<ul id="' + field.short_name + '">'
            for subfield in field:
                frag += self._render_checkbox(subfield, **kwargs)
            frag += "</ul>"
        else:
            if maximise_width:
                clazz += " span11"
                kwargs["class"] = clazz
            frag += field(**kwargs) # FIXME: this is probably going to do some weird stuff

            # FIXME: field.value isn't always set
            #if field.value in extra_input_fields.keys():
            #    extra_input_fields[field.value](**{"class" : "extra_input_field"})

        if field.errors:
            frag += '<ul class="errors">'
            for error in field.errors:
                frag += '<li>' + error + '</li>'
            frag += "</ul>"

        if field.description:
            frag += '<p class="help-block">' + field.description + '</p>'

        frag += "</div>"
        return frag

    def _render_radio(self, field, **kwargs):
        extra_input_fields = kwargs.pop("extra_input_fields", {})

        frag = '<label class="radio" for="' + field.short_name + '">'
        frag += field(**kwargs)
        frag += '<span class="label-text">' + field.label.text + '</span>'

        if field.label.text in extra_input_fields.keys():
            frag += "&nbsp;" + extra_input_fields[field.label.text](**{"class" : "extra_input_field"})

        frag += "</label>"
        return frag


    def _render_checkbox(self, field, **kwargs):
        extra_input_fields = kwargs.pop("extra_input_fields", {})

        frag = "<li>"
        frag += field(**kwargs)
        frag += '<label for="' + field.short_name + '">' + field.label.text + '</label>'

        if field.label.text in extra_input_fields.keys():
            frag += "&nbsp;" + extra_input_fields[field.label.text](**{"class" : "extra_input_field"})

        frag += "</li>"
        return frag

"""