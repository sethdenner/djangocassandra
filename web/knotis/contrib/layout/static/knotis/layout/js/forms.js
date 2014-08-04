(function($) {
    $.fn.ajaxform = function(options) {
        var settings = $.extend({
            done: function(data, status, jqxhr) {},
            fail: function(jqxhr, status, error) {},
            always: function() {},
            method: 'post'
        }, options);
        
        return this.each(function(){
            $(this).unbind('submit').submit(function(event) {
                event.preventDefault();

                var $form = $(this);
                var data = $form.serialize();
                if (data) {
                    data += '&';

                } else {
                    data = '';

                }
                data += 'format=json';

                $form.find('input, button').prop('disabled', true);

                $.ajax({
                    type: settings.method,
                    url: this.action,
                    data: data,
                    success: function(data, status, jqxhr) {
                        $form.find('.modal-body p[class*="text-"]').remove();
                        $form.find('input').next('span.help-inline').remove();
                        $form.find('.control-group').removeClass(
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
                                $form.find('.modal-body').prepend(
                                    '<p class="text-error">' + errors['no-field'] + '</p>'
                                );

                            }

                        } 

                    },
                    dataType: 'json'
                }).done(settings.done).fail(settings.fail).always(function() {
                    $form.find('input, button').prop('disabled', false);
                    settings.always();

                });

            });

        });

    };

})(jQuery);