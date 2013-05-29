(function($) {
    $('#id-login-form').submit(function(event) {
        event.preventDefault();
        
        var $form = $(this)
        $.post(
            this.action,
            $form.serialize(),
            function(data, status, jqxhr) {
                $('#id-login-form .modal-body p[class*="text-"]').remove();
                $('#id-login-form input').next('span.help-inline').remove();
                $('#id-login-form .control-group').removeClass(
                    'error warning info success'
                );

                var errors = data.errors;
                if (errors) {
                    $.each(errors, function(field, message) {
                        var $input = $('input[name=' + field + ']');
                        if (!$input.length) return true;

                        $input.after(
                            '<span class="help-inline">' + message + '</span>'
                        );
                        $input.parent().parent().addClass('error');

                    });
                    
                    if (errors['no-field']) {
                        $('#id-login-form .modal-body').prepend(
                            '<p class="text-error">' + errors['no-field'] + '</p>'
                        );

                    }

                 } else {
                     window.location = '/';

                 }

                var message = data.message;
                if (message) {
                }
            },
            'json'
        ).fail(function(jqxhr, status, error) {
            alert(status);

        });

    });

})(jQuery);