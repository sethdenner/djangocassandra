;

(function($) {
    "use strict";

    $('[data-id=id-redeem-pin]').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                var no_field = data.errors['no-field'];
                if (no_field) {
                    $('p#error-text').html(no_field);
                    $('div.error-row').show('fast');
                }
                return;
            }
            var next_url = data.next ? data.next : '/';
            window.location = next_url;
        }
    });
})(jQuery);
