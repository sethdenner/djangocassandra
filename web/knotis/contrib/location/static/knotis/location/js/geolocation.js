;


(function($) {
    "use strict";

    update_location();

    function register_location(position) {
        var had_position = ($.cookie('latitude') && $.cookie('longitude'));

        console.log('latitude ' + position.coords.latitude);
        console.log('longitude ' + position.coords.longitude);
        console.log('accuracy ' + position.coords.accuracy);

        $.cookie('latitude', position.coords.latitude);
        $.cookie('longitude', position.coords.longitude);
        $.cookie('accuracy', position.coords.accuracy);

        if(!had_position) {
            window.location.reload();
        }
    }

    function broken_locaction(position_error) {
        console.log("No Location! " + position_error);
    }

    function update_location() {
        var thirty_minutes = 1000*60*30;
        var five_minutes = 1000*60*5;

        var geo_options = {
            enableHighAccuracy: true,
            maximumAge        : thirty_minutes,
            timeout           : five_minutes
        };

        if ("geolocation" in navigator) {
            var geo_id = navigator.geolocation.watchPosition(
                register_location,
                broken_locaction,
                geo_options
            );
        }
    }



})(jQuery);
