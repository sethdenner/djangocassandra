(function($) {
    $('#admin_list_controls').ajaxform({
        done: function(data, status, jqxhr) {
            $(".admin_list_entry").remove();
            var activity_results = $('#admin_list_results');
            $.each(data.activities, function(key, value){
                var pos_num = key + data.start
                var activity_record = '<div class="admin_list_entry">'
                                    + '<div class="admin_list_tag">'
                                    + pos_num
                                    + '</div>'
                                    + '<div class="admin_list_value">'
                                    + value
                                    + '</div>';
                activity_results.append(activity_record);
                
            });
        }
    });












})(jQuery);
