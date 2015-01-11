jQuery(document).ready(function($) {
    $.extend(octopus, {
        crud: {
            create : function(params) {
                var dataobj = params.dataobj;
                var objtype = params.objtype;
                var success_callback = params.success;
                var complete_callback = params.complete;
                var error_callback = params.error;

                var postdata = JSON.stringify(dataobj.data);

                $.ajax({
                    type: "POST",
                    contentType: "application/json",
                    dataType: "jsonp",
                    url: octopus.config.crud_endpoint + "/" + objtype,
                    data : postdata,
                    success: success_callback,
                    complete: complete_callback,
                    error: error_callback
                })
            }
        }
    });
});
