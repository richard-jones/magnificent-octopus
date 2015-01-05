jQuery(document).ready(function($) {

    /****************************************************************
     * Application Facetview Theme
     *****************************
     */

    function discoveryRecordView(options, record) {
        var result = options.resultwrap_start;
        result += "<div class='row'>";
        result += "<div class='col-md-12'>";
        result += "<strong style='font-size: 150%'><a href='job/" + record['id'] + "'>" + record["id"] + "</a> - " + record["status"] + "</strong><br>";
        result += "Job Start Timestamp: " + record["start"] + "<br>";
        result += "Created: " + record["created_date"] + "; Last Modified: " + record["last_updated"] + "<br>";
        result += "<strong>Pending: " + record["pending_count"] + "; Success: " + record["success_count"] + "; Errors: " + record["error_count"] + "</strong>";
        result += "</div></div>";
        result += options.resultwrap_end;
        return result;
    }

    var facets = [];
    facets.push({'field': 'status', 'display': 'Status', "open" : true});

    $('#oagmonitor-facetview').facetview({
        debug: false,
        search_url : octopus.config.oagr_query_endpoint,
        page_size : 25,
        facets : facets,
        search_sortby : [
            {'display':'Last Modified','field':'last_updated'},
            {'display':'Date Created','field':'created_date'},
            {'display':'Job Start','field':'start'}
        ],
        searchbox_fieldselect : [
            {'display':'ID','field':'id'}
        ],
        render_result_record : discoveryRecordView,
        fields : ["id", "status", "last_updated", "created_date", "start", "success_count", "error_count", "pending_count"]
    });

});
