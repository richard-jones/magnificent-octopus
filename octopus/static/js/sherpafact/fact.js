var sherpafact = {

    proxy : function(params) {
        var journal_or_issn = params.journal_or_issn;               // a string of some kind
        var funders = params.funders;                               // a list of juliet ids
        var success_callback = params.success ? params.success : function() {};
        var complete_callback = params.complete ? params.complete : function() {};
        var error_callback = params.error ? params.error : function() {};

        var url = octopus.sherpafact.proxy_endpoint

        // make the call to the autocomplete web service
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

};

