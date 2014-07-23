(function($) {
    $('form#id-signup-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                var no_field = data.errors['no-field'];
                if (no_field) {
                    $('p#error-text').html(no_field);
                    $('div.error-row').show('fast');
                }
                return;

            }

            $.ajaxmodal({
                href: '/auth/signup/success/',
                modal_id: 'auth-modal'
            });
        }
    });

})(jQuery);