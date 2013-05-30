(function($) {
    $('#id-login-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                return;

            }

            window.location = '/';

        }
    });

})(jQuery);