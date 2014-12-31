jQuery(document).ready(function($) {
    $.extend(octopus, {
        forms: {

            bindRepeatable: function (params) {
                var button_selector = params.button_selector;
                var list_selector = params.list_selector;
                var entry_prefix = params.entry_prefix;
                var enable_remove = params.enable_remove || false;
                var remove_selector = params.remove_selector;
                var more_callback = params.more_callback;
                var remove_callback = params.remove_callback;

                $(button_selector).click(function (event) {
                    event.preventDefault();

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

                    $("#" + nid).find(".form-group").each(function () {
                        var name = $(this).find(".form-control").attr("name");
                        var bits = name.split("-");
                        bits[bits.length - 2] = max + 1;
                        var newname = bits.join("-");

                        $(this).find(".form-control")
                            .attr("name", newname)
                            .attr("id", newname)
                            .val("");
                        $(this).find("label").attr("for", newname);
                    });

                    if (enable_remove) {
                        $(remove_selector).show()
                            .unbind("click")
                            .click(function (event) {
                                event.preventDefault();
                                $(this).parent().remove();

                                if ($(list_selector).children().size() == 1) {
                                    $(remove_selector).hide();
                                }

                                remove_callback();
                            }
                        );
                    }

                    more_callback();
                })
            }

        }
    });
});

