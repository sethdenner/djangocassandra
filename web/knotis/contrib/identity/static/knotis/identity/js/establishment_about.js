(function($){
    // carousel
    $('#about_carousel').carousel({
        interval: 5000
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
