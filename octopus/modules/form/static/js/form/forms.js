jQuery(document).ready(function($) {
    $.extend(octopus, {
        forms: {

            repeat : function(params) {

                var list_selector = params.list_selector;
                var entry_prefix = params.entry_prefix;
                var enable_remove = params.enable_remove || false;
                var remove_behaviour = params.remove_behaviour || "hide";
                var remove_selector = params.remove_selector;
                var remove_callback = params.remove_callback;

                var source = "";
                var first = true;
                var max = 0;
                var attributes = {};

                $(list_selector).children().each(function () {
                    var bits = $(this).attr("id").split("_");
                    var n = parseInt(bits[bits.length - 1]);
                    if (n > max) {
                        max = n
                    }
                    if (first) {
                        first = false;
                        source = $(this).html();
                        $(this).each(function () {
                            $.each(this.attributes, function () {
                                attributes[this.name] = this.value;
                            });
                        });
                    }
                });

                var nid = entry_prefix + "_" + (max + 1);
                var attrs = "";
                for (var key in attributes) {
                    if (key != "id") {
                        attrs += key + "='" + attributes[key] + "'"
                    }
                }
                var ns = "<div id='" + nid + "' " + attrs + ">" + source + "</div>";

                // append a new section with a new, higher number (and hide it)
                $(list_selector).append(ns);

                $("#" + nid).find(".form-control").each(function () {
                    var name = $(this).attr("name");
                    var bits = name.split("-");
                    bits[1] = max + 1;
                    var newname = bits.join("-");

                    $(this).attr("name", newname)
                        .attr("id", newname)
                        .val("");
                    $("#" + nid).find("label[for=" + name + "]").attr("for", newname);
                });

                if (enable_remove) {
                    if (remove_behaviour === "hide") {
                        $(remove_selector).show();
                    } else if (remove_behaviour === "disable") {
                        $(remove_selector).removeAttr("disabled");
                    }
                    $(remove_selector).unbind("click")
                        .click(function (event) {
                            event.preventDefault();
                            $(this).parents(".repeatable_container").remove();

                            if ($(list_selector).children().size() == 1) {
                                if (remove_behaviour === "hide") {
                                    $(remove_selector).hide();
                                } else if (remove_behaviour === "disable") {
                                    $(remove_selector).attr("disabled", "disabled");
                                }
                            }

                            if (remove_callback) {remove_callback()}
                        }
                    );
                }
            },

            bindRepeatable: function (params) {
                var button_selector = params.button_selector;
                var list_selector = params.list_selector;
                var entry_prefix = params.entry_prefix;
                var enable_remove = params.enable_remove || false;
                var remove_selector = params.remove_selector;
                var remove_behaviour = params.remove_behaviour || "hide";
                var before_callback = params.before_callback;
                var more_callback = params.more_callback;
                var remove_callback = params.remove_callback;

                $(button_selector).click(function (event) {
                    event.preventDefault();

                    if (before_callback) { before_callback() }

                    octopus.forms.repeat({
                        list_selector : list_selector,
                        entry_prefix : entry_prefix,
                        enable_remove : enable_remove,
                        remove_behaviour: remove_behaviour,
                        remove_selector : remove_selector,
                        remove_callback : remove_callback
                    });

                    // each time it is used, re-bind it, as there may now be more
                    // than one "more" button
                    $(button_selector).unbind("click");
                    octopus.forms.bindRepeatable(params);

                    if (more_callback) { more_callback() }
                })
            },

            form2obj : function(params) {
                var form_selector = params.form_selector;
                var formobj = params.form_data_object;
                var xwalk = params.xwalk;
                var record_disabled = params.record_disabled || false;

                // create an object where we can read the raw form data to
                var rawformobj = octopus.dataobj.newDataObj({allow_off_schema: true});

                // create a register of all the form fields which are lists (i.e. repeatable elements)
                var lists = [];

                // for each input field, read it into the raw form object, recording any prefixes of fields which
                // are lists
                $(form_selector).find(":input").each(function() {
                    // if the field is disabled, and disabled field reading is off, skip it
                    if ($(this).attr("disabled") && !record_disabled) {
                        return
                    }

                    var name = $(this).attr("name");
                    if (name) {
                        // get the input type if it has one
                        var type = $(this).attr("type");

                        // get the actual value of the field
                        var val = $(this).val();
                        var storable = false;
                        if (val) {
                            storable = true;
                        }

                        // now adjust based on the type
                        // if it is a checkbox, we want the boolean value, not the actual value
                        if (type && type === "checkbox") {
                            val = $(this).is(":checked");
                            storable = true;
                        }

                        if (storable) {
                            var bits = name.split("-");
                            if (bits.length > 1) {
                                if ($.inArray(bits[0], lists) === -1) {
                                    lists.push(bits[0]);
                                }
                            }
                            var path = bits.join(".");
                            rawformobj.set_field(path, val);
                        }
                    }
                });

                // create an object where we will build the refined form object
                if (!formobj) {
                    formobj = octopus.dataobj.newDataObj({allow_off_schema: true});
                }

                // for each list field, read the data out of the raw form and put it into the refined
                // form object in the correct order
                for (var i = 0; i < lists.length; i++) {
                    var struct = rawformobj.get_field(lists[i]);
                    var indices = Object.keys(struct);
                    var nums = [];
                    var keymap = {};
                    for (var j = 0; j < indices.length; j++) {
                        var n = parseInt(indices[j]);
                        nums.push(n);
                        keymap[n] = indices[j];
                    }
                    nums.sort();
                    for (j = 0; j < nums.length; j++) {
                        var key = keymap[nums[j]];
                        var obj = struct[key];
                        formobj.append_field(lists[i], obj);
                    }
                }

                // copy over all the remaining form fields
                var fields = Object.keys(rawformobj.data);
                for (i = 0; i < fields.length; i++) {
                    var f = fields[i];
                    if ($.inArray(f, lists) === -1) {
                        formobj.set_field(fields[i], rawformobj.get_field(fields[i]));
                    }
                }

                // if a crosswalk is specified, run it
                if (xwalk) {
                    formobj = xwalk(formobj);
                }

                return formobj;
            },

            obj2form : function(params) {
                var form_selector = params.form_selector;
                var formobj = params.form_data_object;
                var xwalk = params.xwalk;

                // create an object where we can read the raw form data to
                var rawformstruct = octopus.dataobj.newDataObj({allow_off_schema: true});

                // create a register of all the form fields which are lists (i.e. repeatable elements)
                var lists = [];

                // read all of the value bearing input fields into a form structure
                $(form_selector).find(":input").each(function() {
                    var name = $(this).attr("name");
                    if (name) {
                        var bits = name.split("-");
                        if (bits.length > 1) {
                            if ($.inArray(bits[0], lists) === -1) {
                                lists.push(bits[0]);
                            }
                        }
                        var path = bits.join(".");
                        rawformstruct.set_field(path, $(this));
                    }
                });

                var formstruct = octopus.dataobj.newDataObj({allow_off_schema: true});

                // for each list field, read the data out of the raw form and put it into the refined
                // form object in the correct order
                for (var i = 0; i < lists.length; i++) {
                    var struct = rawformstruct.get_field(lists[i]);
                    var indices = Object.keys(struct);
                    var nums = [];
                    var keymap = {};
                    for (var j = 0; j < indices.length; j++) {
                        var n = parseInt(indices[j]);
                        nums.push(n);
                        keymap[n] = indices[j];
                    }
                    nums.sort();
                    for (j = 0; j < nums.length; j++) {
                        var key = keymap[nums[j]];
                        var obj = struct[key];
                        formstruct.append_field(lists[i], obj);
                    }
                }

                // copy over all the remaining form fields
                var fields = Object.keys(rawformstruct.data);
                for (i = 0; i < fields.length; i++) {
                    var f = fields[i];
                    if ($.inArray(f, lists) === -1) {
                        formstruct.set_field(fields[i], rawformstruct.get_field(fields[i]));
                    }
                }

                // now map the incoming object values to the form fields, populating their values
                for (i = 0; i < fields.length; i++) {
                    var f = fields[i];
                    if ($.inArray(f, lists) === -1) {
                        // if just a flat field, just copy the value over to the element
                        var el = formstruct.get_field(f);
                        var val = formobj.get_field(f);
                        el.val(val);
                    } else {
                        // if it's a list instead, get the list of groups of fields, then for each object in
                        // order map the values to the form elements
                        var elsetlist = formstruct.get_field(f);
                        var objlist = formobj.get_field(f);
                        if (objlist) {
                            for (var j = 0; j < objlist.length; j++) {
                                var elset = elsetlist[j];
                                var obj = objlist[j];
                                var subfields = Object.keys(obj);
                                for (var k = 0; k < subfields.length; k++) {
                                    var sf = subfields[k];
                                    elset[sf].val(obj[sf]);
                                }
                            }
                        }
                    }
                }
            }

        }
    });
});

