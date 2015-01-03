# Form

This module contains a variety of tools to make form handling easier

## Form Context

The Form Context allows you to re-use forms in different contexts in different parts of your application, and maintain
clean separation of the logic that drives the processing of those forms, while maximising code re-use.

### Outline

It binds together a number of key aspects:

1. The WTForms form definition itself
2. A Renderer which knows details of how that form should be presented to the user
3. A Jinja template that the renderer will be called from
4. The original system object that the form relates to (known as the "source")
5. The resulting system object after it has been edited via the form (known as the "target")
6. A mapping between the source and the form
7. A mapping between the form + source and the target

It implements the following lifecycle:

1. Create a Form Context from one of the following combinations of parameters:
    a. No parameters - a blank form with no backing data
    b. The original system object (source)
    c. The form data alone
    d. The original system object (source) and the form data
2. The Form Context constructs its internal state as follows:
    a. If no parameters are passed, a blank form object will be created
    b. If the source alone is passed, it will be crosswalked using a mapping you must provide, to create a populated form object
    c. If the form data alone is passed, a populated form object will be created
    d. If both he original source and the form data are passed, a populated form object will be created from the form data, and the source will be stored for reference
3. The caller calls FormContext.render_template().  This renders the template specified in your FormContext instance and returns the resulting string (which can in turn be returned by a flask route to the end user)
    a. The template may call FormContext.render_field_group("field_group_name"), which returns a string representation of that portion of the form (see details on the Renderer below for info about field groups)
4. The end user submits the form
5. The caller calls FormContext.validate(), which validates the form input from the end user with the standard WTForms validation mechanism, and then stores information about error fields in the Renderer
    a. If there is a validation failure, and the caller decides to re-deliver the form to the user for corrections, the renderer will present the errors as well.
6. The caller calls FormContext.finalise(), which does the following:
    a. Crosswalks the form data to the target system object, using a mapping you must provide
    b. Patches the target with any data from the source that must be carried over (e.g. created dates, etc), using a process you must define
    c. Any other operations you want to add to the process, such as a call to save() on the target at the end

### Implementation

Implement your forms using WTForms as usual, and then create a subclass of the **octopus.modules.form.context.FormContext**
which implements the relevant methods.  See the source for more details, but in brief you will want to implement some or
all of the following

* make_renderer - This will be called during init, and must populate the self.render property
* set_template - This will be called during init, and must populate the self.template property with the path to the jinja template
* pre_validate - This will be run before validation against the form is run.  Use it to patch the form with any relevant data, such as fields which were disabled
* blank_form - This will be called during init, and must populate the self.form property with an instance of the form in this context, based on no originating source or form data
* data2form - This will be called during init, and must convert the form_data into an instance of the form in this context, and write to self.form
* source2form - This will be called during init, and must convert the source object into an instance of the form in this context, and write to self.form
* form2target - Convert the form object into a the target system object, and write to self.target
* patch_target - Patch the target with data from the source.  This will be run by the finalise method (unless you override it)

For example:

```python
class MyFormContext(FormContext):
    def make_renderer(self):
        self.renderer = MyRenderer()

    def set_template(self):
        self.template = "my_form.html"

    def pre_validate(self):
        self.form.some_disabled_field.data = "a value"

    def blank_form(self):
        self.form = MyForm()

    def data2form(self):
        self.form = MyForm(formdata=self.form_data)

    def source2form(self):
        self.form = MyForm(data=MyFormXWalk.obj2form(self.source))

    def form2target(self):
        self.target = MyFormXWalk.form2obj(self.form)

    def patch_target(self):
        self.target.some_property = self.source.some_property
```

You should also create a subclass of the **octopus.modules.form.context.Renderer**, which knows which fields to render in what order, and with what additional properties.

This is done primarily by populating the FIELD_GROUPS member variable, which has the following structure:

```python
self.FIELD_GROUPS = {
    "<group_name>" : {
        "helper" : "<helper name>",
        "wrappers" : ["<helper wrappers>"],
        "label_width" : <span of label>,
        "control_width" : <span of control>,
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
```

This section of the object describes which fields are part of a logical group on a page, what physical rendering mechanism to use (see below), and the parameters to pass in to the physical renderer.

For example:

```python
class MyRenderer(Renderer):
    def __init__(self):
        super(MyRenderer, self).__init__()

        self.FIELD_GROUPS = {
            "basic_info" : {
                "helper" : "bs3_horizontal",
                "wrappers" : ["first_error", "container"],
                "label_width" : 4,
                "control_width" : 8,
                "fields" : [
                    {"ref" : {"attributes" : {"data-parsley-required" : "true"}}},
                    {"description" : {}},
                ]
            },
            "expenses" : {
                "helper" : "bs3_horizontal",
                "wrappers" : [],
                "label_width" : 4,
                "control_width" : 8,
                "fields" : [
                    {
                        "expenses" : {
                            "fields" : [
                                {"ref" : {}},
                                {"amount" : {"attributes" : {"class" : "input-small", "data-parsley-type" : "number"}}},
                                {"allocate_to" : {}}
                            ]
                        }
                    }
                ]
            }
        }
```

This defines two field groups: "basic_info", and "expenses".  The first group uses the bs3_horizontal helper, with the "first_error" and "container"
wrappers - these are references to the code that will actually do the final rendering.  It then contains a list of 2 fields (in the order that they
should be rendered), one of which contains "attributes" which will be attached to the resulting form input field (and which defines the javascript/parsley
validation requirements in this particular case).

The physical renderers are in **octopus.modules.form.helper**, and can be accessed via a Factory which will construct the relevant render mechanism for you.

For example, in the "basic_info" FIELD_GROUP above, the factory is called as follows:

```python
fh = helper.FormHelperFactory.get(group_def.get("helper"), group_def.get("wrappers"))
```

The form helper returned is a stack of Decorators implementing the various shell pieces of the final render, ultimately culminating in the Bootstrap3 Horizontal Form rendering code.

To use the Renderer and the FIELD_GROUPS, in your Jinja template simply call the render_field_group method in context (remember to turn autoescape off).

For example:

```html
<form class="form-horizontal" id="payment-form">
    <div class="row">
        <div class="col-md-6">
            {% autoescape off %}
            {{ form_context.render_field_group("basic_info") }}
            {% endautoescape %}
        </div>
    </div>
</form>
```html

To serve/process your form do ....
