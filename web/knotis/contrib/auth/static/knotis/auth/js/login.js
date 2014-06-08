(function($) {
    $('#id-login-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                var no_field = data.errors['no-field'];
                if (no_field) {
                    $('p#error-text').html(no_field);
                    $('div.error-row').show('fast');
                }

                $('a#resend_validation_link').click(function(event){
                    event.preventDefault();
                    event.stopPropagation();
                    $.get(this.href, function(data, status, jqxhr) {
                        $('p#error-text').html('Your validation email has been sent.');
                        $('div.error-row').show('fast');
                        
                    });
                });
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

    $('form#id-login-form a#id-forgot-link').click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        $.ajaxmodal({
            href: $(this).attr('href'),
            modal_id: 'auth-modal'
        });
    });

})(jQuery);
