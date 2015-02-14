(function($) {
    $(function () {
        var upload_logo = function(event) {
            event.preventDefault();

            var identity_id = $('div#id-identity-id').attr('data-identity-id');

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
                        primary: true,
                        done: function(data) {
                            if (data.status == 'success') {
                                $img = $('[data-id=id-data-profile-badge]')
                                $img.attr('src', data.image_url);
                            } else if (data.status == 'failure') {

                            } else {
                            // Invalid Status
                            }
                        },
                        related_object_id: identity_id,
                        context: 'profile_badge',
                        jcrop_box_width: 560,
                        image_max_height: 400,
                        image_max_width: 500,
                    });
                }
            });

        };

        $('.change-profile-badge-link').click(upload_logo);

        // BANNER EDITING

        $('a.change-profile-cover-link').click(function(event){
            event.preventDefault();
            var identity_id = $('#id-identity-id').attr('data-identity-id');

            $.ajaxmodal({
                href: '/image/upload',
                modal_settings: {
                    backdrop: 'static'
                },
                on_open: function(data, status, request){

                    $('#file-uploader').sickle({
                        do_upload: true,
                        params: {
                            type: 'image'
                        },
                        aspect: 5.12,
                        related_object_id: identity_id,
                        context: 'profile_banner',
                        image_max_height: 400,
                        image_max_width: 500,
                        primary: true,
                        done: function(data){
                            $('modal-box').modal('hide');
                            $('[data-id=id-data-profile-cover]').css(
                                'background-image',
                                'url("' + data.image_url + '")');
                        },
                        jcrop_box_width: 560
                    });
                }
            });
        });

        $('button.edit_about').click(function(event){
            $('#about-me .viewUser').hide();
            $('#about-me .editUser').show();
        });

        $('button.close_edit_about').click(function(){
            $('#about-me .viewUser').show();
            $('#about-me .editUser').hide();
        });
    });
})(jQuery);
