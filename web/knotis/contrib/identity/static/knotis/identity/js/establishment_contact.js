(function($){
    var latLng = new google.maps.LatLng(parseFloat($('#establishment-contact-loc-details').attr('data-latitude')),
					 parseFloat($('#establishment-contact-loc-details').attr('data-longitude')));

    var initialize = function(){
        var mapOptions = {
            center: latLng,
            zoom: 10,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById('map'), mapOptions);

	var markerOptions = {
	        position: latLng,
	        map: map
	    };
	var marker = new google.maps.Marker(markerOptions);
    }
    
    google.maps.event.addDomListener(window, 'load', initialize);
})(jQuery);
