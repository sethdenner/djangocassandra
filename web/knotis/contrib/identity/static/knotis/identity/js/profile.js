(function($) {

    var upload_logo = function(event) {
        event.preventDefault();

        var identity_id = $('div#id-identity-id').attr('data-identity-id')

        $.ajaxmodal({
            href: '/image/upload/',
            modal_settings: {
                backdrop: 'static'
            },
            on_open: function(data, status, request) {
                $('#file-uploader').sickle({
                    do_upload: true,
                    params: {
                        type: 'image',
                    },
                    aspect: 1,
                    done: function(data) {
                        if (data.status == 'success') {
                            
                        } else if (data.status == 'failure') {
                            
                        } else {
                            // Invalid Status
                        }
                    },
                    related_object_id: identity_id,
                    context: 'profile_badge',
                    jcrop_box_width: 560
                });
            }
        })

    };

    $('div#id-profile-cover img[data-add-image]').click(upload_logo);
    $('div#id-profile-cover img[data-edit-image]').click(upload_logo);

})(jQuery);
