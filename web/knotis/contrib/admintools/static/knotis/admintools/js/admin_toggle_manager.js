(function($) {
    $('#admin_become_manager_button').ajaxform({
         done: function(query_response, status, jqxhr) {location.reload(true)}
    });

})(jQuery);
