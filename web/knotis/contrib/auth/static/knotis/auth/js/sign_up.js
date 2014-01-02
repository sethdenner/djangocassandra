(function($) {
    $('#id-signup-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                return;

            }

            $.ajaxmodal({
                href: '/auth/signup/success/',
                modal_id: 'auth-modal'
            });

        }
    });
    
    $('form#id-signup-form #id-login-link').click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        $.ajaxmodal({
            href: $(this).attr('href'),
            modal_id: 'auth-modal'
        });
    });

})(jQuery);