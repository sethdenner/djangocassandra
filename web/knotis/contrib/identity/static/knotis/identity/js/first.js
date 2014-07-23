(function($) {
    $.ajaxmodal({
        href: '/identity/first/',
        modal_settings: {
            backdrop: 'static',
            keyboard: false,
        },
        on_open: function(data, status, request) {
            $('#id-individual-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (data.errors) {
                        alert('There was an error setting your name.');
                        return;
                    }

                    $('#modal-box').modal('hide');
                    $('#id-current-identity-name').text(data.data.individual_name);
                }
            });

        }
    });

})(jQuery);
