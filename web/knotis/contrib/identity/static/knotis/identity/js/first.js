(function($) {
    $.ajaxmodal({
        href: '/identity/first/',
        modal_settings: {
            backdrop: 'static',
            keyboard: false,
        },
        modal_id: 'first-id',
        on_open: function(data, status, request) {
            $('#id-individual-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (data.errors) {
                        alert('There was an error setting your name.');
                        return;
                    }

                    $('#id-current-identity-name').text(data.data.individual_name);
                    $('#first-id').modal('hide');
                }
            });

        }
    });

})(jQuery);
