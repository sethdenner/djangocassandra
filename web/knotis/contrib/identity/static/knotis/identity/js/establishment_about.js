(function($){
    // carousel
    $('#about_carousel').carousel({
        interval: 5000
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

    // display the map on the about page. 
    var latLng = new google.maps.LatLng(parseFloat($('#establishment-contact-loc-details').attr('data-latitude')),
					 parseFloat($('#establishment-contact-loc-details').attr('data-longitude')));

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
        var map = new google.maps.Map(document.getElementById('about-map'), mapOptions);

	    var markerOptions = {
	        position: latLng,
	        map: map
	    };
	    var marker = new google.maps.Marker(markerOptions);
        map.setZoom(16);
    }
    
    google.maps.event.addDomListener(window, 'load', initialize);

})(jQuery);
