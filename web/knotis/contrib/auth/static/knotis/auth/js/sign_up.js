(function($) {
    $('#id-signup-form').submit(function(event) {
        event.preventDefault();
        
        var $form = $(this)
        $.post(
            this.action,
            $form.serialize(),
            function(data, status, jqxhr) {
                $('#id-signup-form input').next('span.help-inline').remove();
                $('#id-signup-form .control-group').removeClass(
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

                 } else {
                     window.location = '/';

                 }
            },
            'json'
        ).fail(function(jqxhr, status, error) {
            alert(status);

        });

    });

})(jQuery);