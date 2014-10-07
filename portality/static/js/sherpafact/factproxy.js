function sherpaFact(params) {
    var journal_or_issn = params.journal_or_issn;               // a string of some kind
    var funders = params.funders;                               // a list of juliet ids
    var endpoint = params.endpoint;
    var success_callback = params.success ? params.success : function() {};
    var complete_callback = params.complete ? params.complete : function() {};
    var error_callback = params.error ? params.error : function() {};

    // make the call to the autocomplete web service
    $.ajax({
        type: "get",
        url: endpoint,
        data: {journal_or_issn: journal_or_issn, funders: funders},
        dataType: "jsonp",
        success: success_callback,
        complete: complete_callback,
        error: error_callback
    });
}