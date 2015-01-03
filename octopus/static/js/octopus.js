var octopus = {
    display : {
        hidden : {},

        hideOffScreen : function(selector) {
            var el = $(selector);
            if (selector in this.hidden) { return }
            this.hidden[selector] = {"position" : el.css("position"), "margin" : el.css("margin-left")};
            $(selector).css("position", "absolute").css("margin-left", -9999);
        },

        bringIn : function(selector) {
            var pos = this.hidden[selector].position;
            var mar = this.hidden[selector].margin;
            $(selector).css("position", pos).css("margin-left", mar);
            delete this.hidden[selector];
        }
    },

    dataobj : {
        newDataObj : function(params) {
            var F = function() {};
            F.prototype = octopus.dataobj.DataObj;
            var dobj = new F();
            if (params.raw) {
                dobj.data = params.raw;
            }
            if (params.schema) {
                dobj.schema = params.schema;
            }
            return dobj;
        },

        DataObj : {
            data : {},
            schema : {},

            set_field : function(field, value) {
                var cfg = this.schema[field];
                if (cfg.type === "single") {
                    this.set_single(cfg, value);
                }
            },

            set_single : function(cfg, value) {
                // set some default values for the config
                if (!cfg.hasOwnProperty("allow_none")) {
                    cfg.allow_none = true;
                }

                // reject disallowed undefineds
                if (!value && !cfg.allow_none) {
                    throw "undefined not allowed at " + cfg.path;
                }

                // coerce the value if it not undefined
                if (cfg.coerce && value !== undefined) {
                    value = cfg.coerce(value);
                }

                // is the value one of the allowed values
                if (cfg.allowed_values && !$.inArray(value, cfg.allowed_values)) {
                    throw "value" + value + " is not permitted at " + cfg.path;
                }

                // check the value is in the allowed range
                if (cfg.allowed_range) {
                    var lower = cfg.allowed_range.lower;
                    var upper = cfg.allowed_range.upper;
                    if ((lower && value < lower) || (upper && value > upper)) {
                        throw "value " + value + " is outside the allowed range" + lower + " - " + upper;
                    }
                }

                // set the value at the path
                this.set_path(cfg.path, value);
            },

            set_path : function(path, value) {
                var parts = path.split(".");
                var context = this.data;

                for (var i = 0; i < parts.length; i++) {
                    var p = parts[i];

                    if (!context.hasOwnProperty(p) && i < parts.length - 1) {
                        context[p] = {};
                        context = context[p];
                    } else if (context.hasOwnProperty(p) && i < parts.length - 1) {
                        context = context[p];
                    } else {
                        context[p] = value;
                    }
                }
            }
        }
    }
};
