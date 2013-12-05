(function($) {
    $(function() {
        $('#id-forgot-form').ajaxform({
            done: function(data, status, jqxhr) {
                if (data.errors) {
                    return;
                }
            }
        });

        $('form#id-forgot-form button#id-login-button').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            $.ajaxmodal({
                href: $(this).attr('href'),
                modal_id: 'auth-modal'
            });
        });
    });
})(jQuery);