(function($) {

    $('div#id-profile-cover img[data-add-image]').click(function(event) {
        event.preventDefault();

        $('#modal-box').modal({
            backdrop: 'static'
        });

        var identity_id = $('div#id-identity-id').attr('data-identity-id')

        $.get(
            '/image/upload/?object_id=' + encodeURIComponent(identity_id),
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
                        id: identity_id,
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

                });

            }

        );

    });

})(jQuery);