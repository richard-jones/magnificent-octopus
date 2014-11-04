jQuery(document).ready(function($) {
    $.extend(octopus, {
        esac : {

            compoundAutocomplete: function (params) {
                var q = params.q;
                var size = params.size ? params.size : 10;
                var type = params.type;
                var success_callback = params.success ? params.success : function () {};
                var complete_callback = params.complete ? params.complete : function () {};
                var error_callback = params.error ? params.error : function () {};

                var url = octopus.config.es_compound_endpoint + "/" + type

                // make the call to the autocomplete web service
                $.ajax({
                    type: "get",
                    url: url,
                    data: {q: q, size: size},
                    dataType: "jsonp",
                    success: success_callback,
                    complete: complete_callback,
                    error: error_callback
                });
            },

            bindCompoundAutocomplete: function (params) {
                var selector = params.selector;
                var minimumInputLength = params.minimumInputLength || 3;
                var placeholder = params.placeholder || "";
                var type = params.type;
                var format = params.format || function (result) {
                    return {id: result.term, text: result.term}
                };
                var allow_clear = params.allow_clear || true

                function initSel(element, callback) {
                    var data = {id: element.val(), text: element.val()};
                    callback(data);
                }

                function successFunctionClosure(query) {
                    function successFunction(resp) {
                        var data = {results: []};
                        for (var i = 0; i < resp.length; i++) {
                            var r = resp[i];
                            data.results.push(format(r))
                        }
                        query.callback(data);
                    }

                    return successFunction
                }

                function queryFunction(query) {
                    octopus.esac.compoundAutocomplete({
                        q: query.term,
                        type: type,
                        success: successFunctionClosure(query)
                    })
                }

                $(selector).select2({
                    minimumInputLength: minimumInputLength,
                    placeholder: placeholder,
                    query: queryFunction,
                    initSelection: initSel,
                    allowClear: allow_clear
                });
            }
        }
    });
});
