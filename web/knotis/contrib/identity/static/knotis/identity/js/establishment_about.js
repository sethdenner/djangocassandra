(function($){
    // carousel
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


    if (!String.prototype.trim) {
	String.prototype.trim = function () {
	    return this.replace(/^\s+|\s+$/g, '');
	};
    }    


    // endpoint editing
    var comparator = function($element){
	var init = ($element.attr('data-initial-value') || '').trim();
	var current = ($element.val() || '').trim();
	if(init != current){
	    return current;
	}

	return '';
    };

    if (!String.prototype.startsWith) {
	Object.defineProperty(String.prototype, 'startsWith', {
	    enumerable: false,
	    configurable: false,
	    writable: false,
	    value: function (searchString, position) {
		position = position || 0;
		return this.indexOf(searchString, position) === position;
	    }
	});
    }

    $('a.edit_about').click(function(event){
	$('#about-us>.toggleable').toggle();

	// prepopulate endpoints
	$('.edit-endpoint:not(.description):not(#business-address)').each(function(idx, element){
	    $(element).val($(element).attr('data-initial-value') || '');
	});
	
	// submit form handler
	$('#submit-business-info').click(function(e){
	    e.preventDefault();
	    e.stopPropagation();
	    
	    // collect form info
	    var changed_endpoints = {};
	    var changed_name;
	    var changed_description;

	    var business_id = $('#id-business-id').val();

	    $('.edit-endpoint').each(function(idx, element){
		var $element = $(element);
		var id = $element.attr('id');
		
		var changed = comparator($element);
		if (changed){
		    if(id.startsWith('endpoint')){
			changed_endpoints[id] = {
			    'endpoint_id': $element.attr('data-endpoint-id'),
			    'endpoint_type': $element.attr('data-endpoint-type'),
			    'endpoint_value': $element.val()
			};
		    }else if(id == 'business-name'){
			changed_name = $element.val();
		    }else if(id == 'business-description'){
			changed_description = $element.val();
		    }
		}
	    });

	    var info = {};
	    info.business_id = business_id;
	    if(changed_name){
		info.changed_name = changed_name;
	    }
	    info.changed_endpoints = changed_endpoints;
	    info.changed_description = changed_description;

	    $.ajax({
		url: '/identity/update_profile/',
		data: {data:JSON.stringify(info)},
		method: 'POST',
		done: function(response){
		    response = JSON.parse(response);
		    if(response.status.toLowerCase() == 'ok'){
			$('.toggleable').toggle();
			// backpopulate changed info
			for(var endpoint in response.changed_endpoints){
			    $(endpoint.endpoint_id).attr({
				'data-initial-value': endpoint.endpoint_value,
				'data-endpoint-id': endpoint.pk
			    });
			}

			// update social buttons
			for(var endpoint in response.updated_endpoints){
			    if(endpoint.endpoint_type == 4){
				$('.updateable-endpoint.facebook').attr('href', endpoint.url);
			    }
			}

			// TODO Update business name on profile page
			
		    }
		}
	    });
	});
    });

    // address edit
    var $updateable_addresses = $('a#business-address');
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
			    $('a#business-address').attr({
				'data-latitude': data.latitude,
				'data-longitude': data.longitude
			    });
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

})(jQuery);
