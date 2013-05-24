(function($) {
    $('#id-signup-form').submit(function(event) {
        event.preventDefault();
        
        var $form = $(this)
        $.post(
            this.action,
            $form.serialize(),
            function(data, status, jqxhr) {

                var errors = data.errors;
                if (errors) {
                    $.each(errors, function(field, message) {
                        var $input = $('input[name=' + field + ']');
                        $input.after(
                            '<span class="help-inline">' + message + '</span>'
                        );
                        $input.parent().parent().addClass('error');
                    });
                }
            },
            'json'
        ).fail(function(jqxhr, status, error) {
            alert(status);
        });

    });

})(jQuery);