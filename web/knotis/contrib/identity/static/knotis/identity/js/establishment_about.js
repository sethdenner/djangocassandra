(function($){
    $('#about_carousel').carousel({
        interval: 2000
    });
    
    $('a.upload-photo').click(function(event){
	event.preventDefault();
	var identity_id = $(this).attr('data-business-id');
	console.log('identity_id', identity_id);

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
		    aspect: 1.25,
		    related_object_id: identity_id,
		    context: 'business_profile_carousel',
		    primary: false,
		    done: function(data){
			$('modal-box').modal('hide');
		    }
		});
	    }
        });
    });


    // endpoint editing


    $('a.edit_about').click(function(event){
	$('#about-us>.toggleable').toggle();
	$('.edit-endpoint:not(.description)').each(function(idx, $element){
	    $element.val($element.attr('data-initial-value'));
	});
    });

    
})(jQuery);
