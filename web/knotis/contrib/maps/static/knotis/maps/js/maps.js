(function($) {
	
    var pac_container_initialized = false;
    $('div.control-group.geo-input input[type="text"]').keypress(function() {
        if (!pac_container_initialized) {
	    $('.pac-container').css('z-index', '1050');
	    pac_container_initialized = true; 
        }
    });
    
})(jQuery);
