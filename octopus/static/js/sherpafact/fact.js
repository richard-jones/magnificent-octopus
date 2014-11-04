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
            }

        }
    });
});

