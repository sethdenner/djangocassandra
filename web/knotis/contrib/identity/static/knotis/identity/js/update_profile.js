(function($){ 

    // ADDRESS EDITING

    var $updateable_addresses = $('.update-address-link');

    var update_address = function(){
	var $this = $(this);
	$.ajaxmodal({
	    href: '/location_form/',
	    modal_settings: {
		backdrop: 'static',
		keyboard: true
	    },
	    on_open: function(data, status, request){
		$('#id-location-form').ajaxform({
		    done: function(data, status, jqxhr){
			if(!data.errors){
			    $this.text($('#id_address').val());
			    $('#modal-box').modal('hide');
			}
		    }
		});

		$('#id-location-form #address-input #id_address').geocomplete({
		    map: '.map_canvas',
		    location: $this.text(),
		    details: '#id-location-form',
		    detailsAttribute: 'data-geo'
		});

		$('form#id-location-form input#related-id-input').val(
		    $('#id-identity-id').attr('data-identity-id')
		);
	    }
	});

    };


    $updateable_addresses.on('click', update_address);


    // ENDPOINT EDITING

    var $potential_input = $('.editable.establishment-endpoint');
    
    var submit_endpoint = function($elem){
	var identity_id = $elem.attr('data-establishment-id');
	var endpoint_type = $elem.attr('data-endpoint-endpoint-type-name');
	var endpoint_id = $elem.attr('data-endpoint-id');
	
	$.post(
	    '/api/v1/endpoint/',
	    {
		identity_id: identity_id,
		endpoint_type: endpoint_type,
		endpoint_id: endpoint_id,
		value: $elem.text().trim()
	    },
	    function(data){
		$elem.removeAttr('contenteditable');
		if(!data.errors){
		    $elem.blur();
		    $elem.attr('data-endpoint-endpoint-id', data['endpoint-id'])
		}else{
		    $potential_input.one('click', edit_endpoint); 
		}
	    }
	);
    };

    var edit_endpoint = function(){
	var $this = $(this);
	var current_val = $this.text();

	$this.attr('contenteditable', true);

	$this.on('keypress', function(e){
	    if (e.which == 13){
		$this.off('blur');
		submit_endpoint($this);
		e.preventDefault();
	    }
	});

	$this.one('blur', function(e){
	    $this.off('keypress');
	    if($this.text() != current_val){
		submit_endpoint($this);
	    }
	    e.preventDefault();
	});
    };
	
    $potential_input.one('click', edit_endpoint);

    // EDIT NAME
    var $updateable_name = $('.updateable-name');

    var submit_name = function($elem){
	var $this = $(this);
	
	var identity_id = $elem.attr('data-establishment-id');
	var identity_type = $elem.attr('data-identity-type');
	$.ajax({
	    url: '/api/v1/identity/identity/',
	    type: 'PUT',
	    data: {
		id: identity_id,
		name: $elem.text().trim(),
		identity_type: identity_type
	    }
	}).done(function(data){
	    $elem.removeAttr('contenteditable');
	    if(!data.errors){
		$elem.blur();
	    }else{
		$updateable_name.one('click', edit_name);
	    }
	});
    };

    var edit_name = function(){
	var $this = $(this);

	$this.attr('contenteditable', true);

	$this.on('keypress', function(e){
	    if(e.which == 13){
		$this.off('blur');
		submit_name($this);
		e.preventDefault();
	    }
	});

	$this.one('blur', function(e){
	    $this.off('keypress');
	    submit_name($this);
	    e.preventDefault();
	});
    };

    $updateable_name.one('click', edit_name);

    // BANNER EDITING

    $('a.change-profile-cover-link').click(function(event){
	event.preventDefault();
	var identity_id = $('div#id-identity-id').attr('data-identity-id');

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
		    done: function(data){
			$('modal-box').modal('hide');
			$('#profile-header').attr('src', data.image_url);
		    },
            jcrop_box_width: 560
		});		
	    }
	});
    });


    // BADGE EDITING

    $('a.change-profile-badge-link').click(function(event){
	event.preventDefault();
	var identity_id = $('div#id-identity-id').attr('data-identity-id');

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
		    context: 'profile_badge',
		    done: function(data){
			$('modal-box').modal('hide');
			$img = $('#profile-badge');
			$img.attr('src', data.image_url);
		    }
		});		
	    }
	});
    });

    
})(jQuery);
