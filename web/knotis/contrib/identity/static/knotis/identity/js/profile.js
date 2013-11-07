(function($) {

    var upload_logo = function(event) {
        event.preventDefault();

        var identity_id = $('div#id-identity-id').attr('data-business-id')

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
                            
			    // $('modal-box').modal('hide');
			    $img = $('#profile-badge');
			    $img.attr('src', data.image_url);
			    
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

    $('.change-profile-badge-link').click(upload_logo);

    // BANNER EDITING

    $('a.change-profile-cover-link').click(function(event){
	    event.preventDefault();
	    var identity_id = $('#id-identity-id').attr('data-business-id');

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
		            primary: true,
		            done: function(data){
			            $('modal-box').modal('hide');
			            $('#profile-header').attr('src', data.image_url);
		            },
		            jcrop_box_width: 560
		        });		
	        }
	    });
    });

})(jQuery);
