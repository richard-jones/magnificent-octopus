jQuery(document).ready(function($) {
    $.extend(octopus, {
        fragments : {
            cache : {},

            cacheCallbackClosure : function(id, callback) {
                function fragCallback(html) {
                    octopus.fragments.cache[id] = html;
                    callback(html)
                }
                return fragCallback;
            },

            frag : function(params) {
                var frag_id = params.id;
                var callback = params.callback;

                if (octopus.fragments.cache[frag_id]) {
                    callback(octopus.fragments.cache[frag_id]);
                    return
                }

                $.ajax({
                    type: "GET",
                    dataType: "html",
                    url: octopus.config.fragments_endpoint + "/" + frag_id,
                    success: octopus.fragments.cacheCallbackClosure(frag_id, callback)
                });
            }
        }
    });
});
