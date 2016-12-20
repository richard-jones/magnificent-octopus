jQuery(document).ready(function($) {

    $.extend(octopus, {
        account: {
            activeEdges : {},

            newBasicAccount : function(params) {
                var schema = {
                    id : {type : "single", path : "id", coerce: String },
                    created_date : {type : "single", path : "created_date", coerce: String},
                    last_updated : {type : "single", path : "last_updated", coerce: String},

                    email : { type : "single", path : "email", coerce : String},
                    name : { type : "single", path : "name", coerce : String, default_value: "Unknown Name"},
                    org_role : { type : "single", path : "org_role", coerce : String, default_value: "Unknown Role"},
                    organisation : { type : "single", path : "organisation", coerce : String, default_value: "Unknown Organisation"},
                    role : {type: "list", path: "role", coerce: String}
                };

                var BasicAccount = function() {
                    this.data = {};
                    this.schema = {};
                    this.allow_off_schema = false;
                };

                var proto = $.extend(octopus.dataobj.DataObjPrototype, octopus.account.BasicAccountPrototype);
                BasicAccount.prototype = proto;

                var dobj = new BasicAccount();
                dobj.schema = schema;
                if (params) {
                    if (params.raw) {
                        dobj.data = params.raw;
                    }
                }
                return dobj;
            },
            BasicAccountPrototype : {

            },

            newAccountRenderer : function(params) {
                if (!params) { params = {} }
                octopus.account.AccountRenderer.prototype = edges.newRenderer(params);
                return new octopus.account.AccountRenderer(params);
            },
            AccountRenderer : function(params) {
                //////////////////////////////////////////////
                // parameters that can be passed in

                // what to display when there are no results
                this.noResultsText = edges.getParam(params.noResultsText, "No results to display");

                //////////////////////////////////////////////
                // variables for internal state

                // namespace for css classes and ids
                this.namespace = "octopus-account";

                this.draw = function() {
                    var frag = this.noResultsText;
                    if (this.component.results === false) {
                        frag = "";
                    }

                    var results = this.component.results;
                    if (results && results.length > 0) {
                        // list the css classes we'll require
                        var recordClasses = edges.css_classes(this.namespace, "record", this);

                        // now call the result renderer on each result to build the records
                        frag = "";
                        for (var i = 0; i < results.length; i++) {
                            var rec = this._renderResult(results[i]);
                            frag += '<div class="row"><div class="col-md-12"><div class="' + recordClasses + '">' + rec + '</div></div></div>';
                        }
                    }

                    // finally stick it all together into the container
                    var containerClasses = edges.css_classes(this.namespace, "container", this);
                    var container = '<div class="' + containerClasses + '">' + frag + '</div>';
                    this.component.context.html(container);

                    // now bind the "more"/"less" buttons
                    //var moreSelector = edges.css_class_selector(this.namespace, "more-link", this);
                    //edges.on(moreSelector, "click", this, "showMore");

                    //var lessSelector = edges.css_class_selector(this.namespace, "less-link", this);
                    //edges.on(lessSelector, "click", this, "showLess");
                };

                this._renderResult = function(res) {

                    var acc = octopus.account.newBasicAccount({raw: res});
                    var id = edges.objVal("id", res);

                    var userRowClass = edges.css_classes(this.namespace, "user-result", this);

                    // outer container for display (fitting with the tabular style of the facetview)
                    var result = "<tr><td>";

                    result += "<div class='" + userRowClass + "'>";
                    result += "<div class='row'>";

                    // left-hand container for metadata
                    result += "<div class='col-md-10'>";
                    result += "<strong>" + edges.escapeHtml(acc.get_field("email")) + "</strong><br>";
                    result += edges.escapeHtml(acc.get_field("name")) + ", " + edges.escapeHtml(acc.get_field("org_role")) + " at " + edges.escapeHtml(acc.get_field("organisation")) + "<br>";
                    result += "System roles: " + acc.get_field("role").join(", ");
                    result += "</div>";

                    // right-hand container for links out
                    result += "<div class='col-md-2'>";
                    result += '<a href="/account/' + edges.escapeHtml(acc.get_field("email")) + '" class="btn btn-info pull-right" style="margin-top: 15px"><span class="glyphicon glyphicon-pencil"></span>&nbsp;&nbsp;Edit User</a>';

                    // close right-hand container
                    result += "</div>";

                    // close off the overall container
                    result += "</div></div></td></tr>";

                    return result;
                };

            }
        }
    });

    var selector = '#userfacetview';
    var e = edges.newEdge({
        selector: selector,
        template: edges.bs3.newFacetview(),
        search_url: octopus.config.account_list_endpoint,
        manageUrl : false,
        components : [
            // configure the search controller
            edges.newFullSearchController({
                id: "search-controller",
                category: "controller",
                sortOptions : [
                    {"display" : "Email", "field" : "email.exact"},
                    {"display" : "Name", "field" : "name.exact"},
                    {"display" : "Organisation", "field" : "organisation.exact"}
                ],
                fieldOptions : [
                    {'display':'Email','field':'email'},
                    {"display" : "Name", "field" : "name"},
                    {"display" : "Organisation", "field" : "organisation"},
                    {"display" : "Role at Organisation", "field" : "org_role"},
                    {"display" : "System role", "field" : "role"}
                ],
                defaultOperator : "AND",
                renderer : edges.bs3.newFullSearchControllerRenderer({
                    freetextSubmitDelay: -1
                })
            }),
            // the pager, with the explicitly set page size options (see the openingQuery for the initial size)
            edges.newPager({
                id: "top-pager",
                category: "top-pager",
                rederer : edges.bs3.newPagerRenderer({
                    sizeOptions : [10, 25, 50, 100]
                })
            }),
            edges.newPager({
                id: "bottom-pager",
                category: "bottom-pager",
                rederer : edges.bs3.newPagerRenderer({
                    sizeOptions : [10, 25, 50, 100]
                })
            }),
            edges.newSearchingNotification({
                id: "searching-notification",
                category: "searching-notification"
            }),
            edges.newResultsDisplay({
                id: "results",
                category: "results",
                renderer : octopus.account.newAccountRenderer()
            })
        ]
    });

    octopus.account.activeEdges[selector] = e;
});
