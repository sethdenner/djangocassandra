(function($){

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
            if(current == ''){
                return true;
            }

	        return current;
	    }

	    return false;
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

    var endpoint_id_to_type = {
        0: 'email',
        1: 'phone',
        3: 'twitter',
        4: 'facebook',
        5: 'yelp',
        9: 'website',
        10: 'link'
    };

    var endpoint_type_to_id = {
        'email': 0,
        'phone': 1,
        'twitter': 3,
        'facebook': 4,
        'yelp': 5,
        'website': 9,
        'link': 10
    };

    /*
      Takes one updated endpoint of the kind returned in a call to update_profile/ and
      displays the corresponding endpoints on the profile header.
     */
    var header_display_updated_endpoint = function(updated){
        // var endpoint_type_name = endpoint_id_to_type[updated['endpoint_type']];
        var endpoint_id = updated['pk']; 
        // determine whether endpoint type is already displayed
        var $list = $('#id-profile-contact>strong>ul');
        var $endpoints = $list.children('[data-endpoint-endpoint-type-name="' + endpoint_id_to_type[updated['endpoint_type']] + '"]');
        if($endpoints.size() == 1){
            var $endpoint = $endpoints;
            $endpoint.attr('href', updated['url']);
            
            if(updated['endpoint_type'] != 4 &&
               updated['endpoint_type'] != 5 &&
               updated['endpoint_type'] != 3){
                $endpoint.text(updated['value']);
            }
            
        }else{
            var text = updated['value'];

            if(updated['endpoint_type'] == 4){
                text = 'Facebook';
            }else if(updated['endpoint_type'] == 5){
                text = 'Yelp';
            }else if(updated['endpoint_type'] == 3){
                text = 'Twitter';
            }

            var href = updated['url'];
            var establishment_id = $('id-identity-id').attr('data-identity-id');
            var endpoint_id = updated['pk'];
            var endpoint_type_name = endpoint_id_to_type[updated['endpoint_type']];

            var $endpoint = $('<li></li>');
            $endpoint.attr({
                'class': 'establishment-endpoint',
                'data-establishment-id': establishment_id,
                'data-endpoint-endpoint-id': endpoint_id,
                'data-endpoint-endpoint-type-name': endpoint_type_name
            });
            $endpoint_link = $('<a></a>');
            $endpoint_link.text(text);
            $endpoint_link.attr({
                'href': href
            });
            $endpoint.append($endpoint_link);
            $list.append($endpoint);
        }
    };

    /*
      Displays endpoint elements on the edit form.
     */
    var form_display_updated_endpoint = function(updated){
        var $form_endpoint = $('[data-endpoint-type="' + updated['endpoint_type'] + '"]');
        
        var new_value = updated['value'];
        var endpoint_id = updated['pk'] || $form_endpoint.attr('data-endpoint-id');

        $form_endpoint.attr({
            'data-initial-value': new_value,
            'data-endpoint-id': endpoint_id
        });
        // $form_endpoint.val(new_value);
    };

    $('a.edit_about').click(function(event){
	    $('#about-us>.toggleable').show();

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
			            changed_description = $element.val().trim();
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
		        success: function(response){
		            if(response.status == 'ok'){
			            
			            // backpopulate changed info
			            for(var endpoint in response.changed_endpoints){
			                $(endpoint.endpoint_id).attr({
				                'data-initial-value': endpoint.endpoint_value,
				                'data-endpoint-id': endpoint.pk
			                });
			            }

			            // update social buttons
			            for(var i=0; i<response.updated_endpoints.length; i++){
			                var endpoint = response.updated_endpoints[i];
			                if(endpoint.endpoint_type == 4){
                                // update social button
				                $('.updateable-endpoint.facebook').
                                    attr('href', endpoint.url);
			                }
			                if(endpoint.endpoint_type == 5){
                                // update social button
				                $('.updateable-endpoint.yelp').
                                    attr('href', endpoint.url);
			                }
			                if(endpoint.endpoint_type == 3){
                                // update social button
				                $('.updateable-endpoint.twitter').
                                    attr('href', endpoint.url);
			                }
                            
                            form_display_updated_endpoint(response.updated_endpoints[i]);
                            header_display_updated_endpoint(response.updated_endpoints[i]);
			            }

                        for(var i=0; i<response.deleted_endpoints.length; i++){
                            var endpoint = response.deleted_endpoints[i];
                            
                            $('#id-profile-contact>strong>ul>[data-endpoint-endpoint-id=' + endpoint['pk'] + ']').remove();
                            $('#about-us-form>[data-endpoint-type="' + endpoint['endpoint_type'] + ']').val('');
                        }

			            // Update business name on profile page
                        $('.toggleable').hide();			            
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

    // display the map on the about page. 

    // display the map on the about page. 
    var latLng = new google.maps.LatLng(parseFloat($('#establishment-contact-loc-details').attr('data-latitude')),
					                    parseFloat($('#establishment-contact-loc-details').attr('data-longitude')));
    
    var map;
    var initialize = function(){
        var mapOptions = {
            center: latLng,
            zoomControl: false,
            scaleControl: false,
            draggable: false,
            navigationContol: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            zoom: 16
        };
        map = new google.maps.Map(document.getElementById('about-map'), mapOptions);

	    var markerOptions = {
	        position: latLng,
	        map: map
	    };
	    var marker = new google.maps.Marker(markerOptions);
        map.setZoom(16);
    }
    
    google.maps.event.addDomListener(window, 'load', initialize);
    google.maps.event.trigger(map, 'resize');


})(jQuery);
