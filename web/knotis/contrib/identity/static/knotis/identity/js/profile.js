(function($) {

    $('div#id-profile-cover img[data-add-image]').click(function(event) {
        event.preventDefault();

        $('#modal-box').modal({
            backdrop: 'static'
        });

        var identity_id = $('div#id-identity-id').attr('data-identity-id')

        $.get(
            '/image/upload/',
            {},
            function(
                data,
                status,
                jqxhr
            ) {
                $('#modal-box').html(data);
                $('#file-uploader').sickle({
                    do_upload: true,
                    params: {
                        type: 'image'
                    },
                    aspect: 1,
                    done: function(data) {
                        if (data.status == 'success') {
                            
                        } else if (data.status == 'failure') {
                            
                        } else {
                            // Invalid Status
                        }
                    },
                    related_object_id: identity_id

                });

            }

        );

    });

})(jQuery);