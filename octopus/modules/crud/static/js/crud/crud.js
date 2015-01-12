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
            },

            retrieve : function(params) {
                var objtype = params.objtype;
                var id = params.id;
                var success_callback = params.success;
                var complete_callback = params.complete;
                var error_callback = params.error;

                $.ajax({
                    type: "GET",
                    contentType: "application/json",
                    dataType: "jsonp",
                    url: octopus.config.crud_endpoint + "/" + objtype + "/" + id,
                    success: success_callback,
                    complete: complete_callback,
                    error: error_callback
                })
            },

            update : function(params) {
                var dataobj = params.dataobj;
                var objtype = params.objtype;
                var id = params.id;
                var success_callback = params.success;
                var complete_callback = params.complete;
                var error_callback = params.error;

                var putdata = JSON.stringify(dataobj.data);

                $.ajax({
                    type: "PUT",
                    contentType: "application/json",
                    dataType: "jsonp",
                    url: octopus.config.crud_endpoint + "/" + objtype + "/" + id,
                    data : putdata,
                    success: success_callback,
                    complete: complete_callback,
                    error: error_callback
                })
            }
        }
    });
});
