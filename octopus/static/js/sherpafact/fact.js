jQuery(document).ready(function($) {
    $.extend(octopus, {

        sherpafact: {

            proxy: function (params) {
                var journal_or_issn = params.journal_or_issn;               // a string of some kind
                var funders = params.funders;                               // a list of juliet ids
                var success_callback = params.success ? params.success : function () {};
                var complete_callback = params.complete ? params.complete : function () {};
                var error_callback = params.error ? params.error : function () {};

                var url = octopus.config.fact_proxy_endpoint;

                // make the call to the fact proxy web service
                $.ajax({
                    type: "get",
                    url: url,
                    data: {journal_or_issn: journal_or_issn, funders: funders.join(",")},
                    dataType: "jsonp",
                    success: success_callback,
                    complete: complete_callback,
                    error: error_callback
               });
            },

            newFact : function(params) {
                var F = function() {};
                F.prototype = octopus.sherpafact.Fact;
                var fact = new F();
                if (params.raw) {
                    fact.raw = params.raw;
                }
                return fact;
            },

            Fact : {
                raw : {},

                result_count : function() {
                    if (this.raw.control) {
                        return this.raw.control.val_num_journals;
                    }
                },

                journal_name: function() {
                    if (this.raw.journal && this.raw.journal.length > 0) {
                        var j = this.raw.journal[0];
                        return j.val_title;
                    } else {
                        return "";
                    }
                },
                journals : function() {
                    if (this.raw.journal && this.raw.journal.length > 0) {
                        return this.raw.journal;
                    }
                    return [];
                },
                funder_names: function() {
                    if (this.raw.funder && this.raw.funder.length > 0) {
                        var names = [];
                        for (var i = 0; i < this.raw.funder.length; i++) {
                            var f = this.raw.funder[i];
                            if (f.val_name) {
                                names.push(f.val_name);
                            }
                        }
                        return names;
                    }
                    return [];
                },
                issn : function() {
                    if (this.raw.journal && this.raw.journal.length > 0) {
                        var j = this.raw.journal[0];
                        return j.arg_issn;
                    }
                    return "";
                },
                publisher : function() {
                    if (this.raw.journal && this.raw.journal.length > 0) {
                        var j = this.raw.journal[0];
                        return j.val_publisher;
                    }
                    return "";
                },
                juliet_ids : function() {
                    var jids = [];
                    if (this.raw.funder && this.raw.funder.length > 0) {
                        for (var i = 0; i < this.raw.funder.length; i++) {
                            var f = this.raw.funder[i];
                            if (f.arg_juliet_id) {
                                jids.push(f.arg_juliet_id);
                            }
                        }
                    }
                    return jids;
                },

                overall_compliance : function() {
                    if (this.raw.overall && this.raw.overall.arg_overallcompliancecode) {
                        return this.raw.overall.arg_overallcompliancecode;
                    }
                    return "no";
                },
                overall_compliance_msg : function() {
                    if (this.raw.overall && this.raw.overall.val_overallcompliance) {
                        return this.raw.overall.val_overallcompliance;
                    }
                    return "";
                },
                overall_recommendation : function() {
                    if (this.raw.overall && this.raw.overall.val_overallrecommendation) {
                        return this.raw.overall.val_overallrecommendation
                    }
                    return "";
                },
                overall_advice : function() {
                    var oas = [];
                    if (this.raw.overall && this.raw.overall.overalladvice && this.raw.overall.overalladvice.length > 0) {
                        for (var i = 0; i < this.raw.overall.overalladvice.length; i++) {
                            var oa = this.raw.overall.overalladvice[i];
                            if (oa.val_overalladvice) {
                                oas.push(oa.val_overalladvice);
                            }
                        }
                    }
                    return oas;
                },

                gold_compliance : function() {
                    if (this.raw.gold && this.raw.gold.arg_goldcompliancecode) {
                        return this.raw.gold.arg_goldcompliancecode;
                    }
                    return "no";
                },
                gold_compliance_msg : function() {
                    if (this.raw.gold && this.raw.gold.val_goldcompliance) {
                        return this.raw.gold.val_goldcompliance;
                    }
                    return "";
                },
                gold_compliance_reason : function(params) {
                    var link = params.link || false;
                    var linkclass = params.linkclass || "";

                    var reason = "";
                    if (this.raw.gold && this.raw.gold.val_goldreason) {
                        reason = this.raw.gold.val_goldreason;
                    }

                    if (link && this.raw.gold && this.raw.gold.arg_goldreasonlinktext && this.raw.gold.arg_goldreasonlinkurl) {
                        var text = this.raw.gold.arg_goldreasonlinktext;
                        var url = this.raw.gold.arg_goldreasonlinkurl;
                        reason = this._linkify({
                            text : text,
                            url : url,
                            source : reason,
                            linkclass : linkclass
                        });
                    }

                    return reason;
                },
                gold_fee : function() {
                    if (this.raw.gold && this.raw.gold.val_goldfee) {
                        return this.raw.gold.val_goldfee;
                    }
                    return "";
                },
                gold_advice : function() {
                    var gas = [];
                    if (this.raw.gold && this.raw.gold.goldadvice && this.raw.gold.goldadvice.length > 0) {
                        for (var i = 0; i < this.raw.gold.goldadvice.length; i++) {
                            var ga = this.raw.gold.goldadvice[i];
                            if (ga.val_goldadvice) {
                                gas.push(ga.val_goldadvice);
                            }
                        }
                    }
                    return gas;
                },
                gold_confirm : function(params) {
                    var link = params.link || false;
                    var linkclass = params.linkclass || "";

                    var gcs = [];
                    if (this.raw.gold && this.raw.gold.goldconfirm && this.raw.gold.goldconfirm.length > 0) {
                        for (var i = 0; i < this.raw.gold.goldconfirm.length; i++) {
                            var gc = this.raw.gold.goldconfirm[i];
                            if (gc.val_goldconfirm) {
                                var conf = gc.val_goldconfirm;
                                if (link && gc.arg_goldconfirmlinktext && gc.arg_goldconfirmlinkurl) {
                                    conf = this._linkify({
                                        text : gc.arg_goldconfirmlinktext,
                                        url : gc.arg_goldconfirmlinkurl,
                                        source : conf,
                                        linkclass : linkclass
                                    });
                                }
                                gcs.push(conf);
                            }
                        }
                    }
                    return gcs;
                },
                gold_process: function() {
                    var gps = [];
                    if (this.raw.gold && this.raw.gold.goldprocess && this.raw.gold.goldprocess.length > 0) {
                        for (var i = 0; i < this.raw.gold.goldprocess.length; i++) {
                            var gp = this.raw.gold.goldprocess[i];
                            if (gp.val_goldprocess) {
                                gps.push(gp.val_goldprocess);
                            }
                        }
                    }
                    return gps;
                },
                gold_decision : function() {
                    // This method is tricky, so will be carefully explained

                    // this is the parent decision trail object.  All decisions are stored in here, in the order
                    // that they were considered.  In turn each sub-decision has a set of children in the order that they
                    // occurred, and so on.
                    var decision = [];

                    // this is the stack, where we will keep track of the current deepest element in the tree.
                    // we start off with the parent decision trail object at the bottom of the stack
                    var stack = [];
                    stack.push(decision);

                    if (this.raw.gold && this.raw.gold.golddecision && this.raw.gold.golddecision.length > 0) {
                        for (var i = 0; i < this.raw.gold.golddecision.length; i++) {
                            // get the details that we care about for this decision, and make the decision
                            // object with a pre-prepared "children" field
                            var d = this.raw.gold.golddecision[i];
                            var al = d.arg_level;
                            var obj = {"text" : d.val_golddecision, "children" : []};

                            // pop the stack up to the point where the last element in the stack is the parent of
                            // the object's current level (al).  Because there is the parent decision trail object,
                            // the first element of the stack is untouchable, hence the + 1
                            while (al + 1 < stack.length) {
                                stack.pop()
                            }

                            // get the last element in the stack, which is the parent of the current element
                            var context = stack[stack.length - 1];

                            // push this object into the parent
                            context.push(obj);

                            // add the children array of the current object to the stack.  This means if the next
                            // element is a child of this one, it can push itself into that children array.  If it is
                            // not, then the stack will get popped back to the relevant level (see above).
                            stack.push(obj.children);
                        }
                    }
                    return decision;
                },

                green_compliance : function() {
                    if (this.raw.green && this.raw.green.arg_greencompliancecode) {
                        return this.raw.green.arg_greencompliancecode;
                    }
                    return "no";
                },
                green_compliance_msg : function() {
                    if (this.raw.green && this.raw.green.val_greencompliance) {
                        return this.raw.green.val_greencompliance;
                    }
                    return "";
                },
                green_compliance_reason : function(params) {
                    var link = params.link || false;
                    var linkclass = params.linkclass || "";

                    var reason = "";
                    if (this.raw.green && this.raw.green.val_greenreason) {
                        reason = this.raw.green.val_greenreason;
                    }

                    if (link && this.raw.green && this.raw.green.arg_greenreasonlinktext && this.raw.green.arg_greenreasonlinkurl) {
                        var text = this.raw.green.arg_greenreasonlinktext;
                        var url = this.raw.green.arg_greenreasonlinkurl;
                        reason = this._linkify({
                            text : text,
                            url : url,
                            source : reason,
                            linkclass : linkclass
                        });
                    }

                    return reason;
                },
                green_advice : function() {
                    var gas = [];
                    if (this.raw.green && this.raw.green.greenadvice && this.raw.green.greenadvice.length > 0) {
                        for (var i = 0; i < this.raw.green.greenadvice.length; i++) {
                            var ga = this.raw.green.greenadvice[i];
                            if (ga.val_greenadvice) {
                                gas.push(ga.val_greenadvice);
                            }
                        }
                    }
                    return gas;
                },
                green_confirm : function() {
                    var gcs = [];
                    if (this.raw.green && this.raw.green.greenconfirm && this.raw.green.greenconfirm.length > 0) {
                        for (var i = 0; i < this.raw.green.greenconfirm.length; i++) {
                            var gc = this.raw.green.greenconfirm[i];
                            if (gc.val_greenconfirm) {
                                gcs.push(gc.val_greenconfirm);
                            }
                        }
                    }
                    return gcs;
                },
                green_decision : function() {
                    // This method is tricky, so will be carefully explained

                    // this is the parent decision trail object.  All decisions are stored in here, in the order
                    // that they were considered.  In turn each sub-decision has a set of children in the order that they
                    // occurred, and so on.
                    var decision = [];

                    // this is the stack, where we will keep track of the current deepest element in the tree.
                    // we start off with the parent decision trail object at the bottom of the stack
                    var stack = [];
                    stack.push(decision);

                    if (this.raw.green && this.raw.green.greendecision && this.raw.green.greendecision.length > 0) {
                        for (var i = 0; i < this.raw.green.greendecision.length; i++) {
                            // get the details that we care about for this decision, and make the decision
                            // object with a pre-prepared "children" field
                            var d = this.raw.green.greendecision[i];
                            var al = d.arg_level;
                            var obj = {"text" : d.val_greendecision, "children" : []};

                            // pop the stack up to the point where the last element in the stack is the parent of
                            // the object's current level (al).  Because there is the parent decision trail object,
                            // the first element of the stack is untouchable, hence the + 1
                            while (al + 1 < stack.length) {
                                stack.pop()
                            }

                            // get the last element in the stack, which is the parent of the current element
                            var context = stack[stack.length - 1];

                            // push this object into the parent
                            context.push(obj);

                            // add the children array of the current object to the stack.  This means if the next
                            // element is a child of this one, it can push itself into that children array.  If it is
                            // not, then the stack will get popped back to the relevant level (see above).
                            stack.push(obj.children);
                        }
                    }
                    return decision;
                },

                _linkify : function(params) {
                    var text = params.text;
                    var url = params.url;
                    var source = params.source;
                    var linkclass = params.linkclass;

                    var start = source.indexOf(text);
                    var end = start + text.length;
                    return source.substring(0, start) + "<a href='" + url + "' class='" + linkclass + "'>" +
                                source.substring(start, end) + "</a>" + source.substring(end);
                }
            }

        }
    });
});

