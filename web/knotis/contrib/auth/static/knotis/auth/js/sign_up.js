(function($) {
    $('#id-signup-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                return;

            }

            window.location = '/';

        }
    });
    
    $('form#id-signup-form #id-login-link').click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        $.ajaxmodal({
            href: $(this).attr('href'),
            modal_id: 'sign-up-modal'
        });
    });

})(jQuery);