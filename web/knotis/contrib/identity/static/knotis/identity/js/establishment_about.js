(function($){
    $('#about_carousel').carousel({
        interval: 2000
    });
    
    $('a.upload-photo').click(function(event){
	event.preventDefault();
	var identity_id = $('div#id-identity-id').attr('data-business-id');
	
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
		    aspect: 1,
		    related_object_id: identity_id,
		    context: 'business_profile_carousel',
		    primary: true,
		    done: function(data){
			$('modal-box').modal('hide');
		    }
		});
	    }
        });
    });
    
})(jQuery);
