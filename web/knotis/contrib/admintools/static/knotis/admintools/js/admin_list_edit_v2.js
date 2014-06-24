(function($) {
    $('#admin_query_form').ajaxform({
        done: function(data, status, jqxhr) {
            $('.admin_list_entry').remove();
            var results = $('#admin_list_results');
            posting = '<div class="admin_list_entry">'
                    + data
                    + '</div>'
            results.append(posting);
        }

//            $.each(data.users, function(ukey, uvalue) {

    });
    $('#admin_create_form').ajaxform({
//        done: FIX ME LATER TO DISPLAY STATUS
    });



})(jQuery);
