(function($) {
    $('#id-login-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                return;

            }

            window.location = '/';

        }
    });

    $('form#id-login-form #id-signup-link').click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        $.ajaxmodal({
            href: $(this).attr('href'),
            modal_id: 'auth-modal'
        });
    });

})(jQuery);