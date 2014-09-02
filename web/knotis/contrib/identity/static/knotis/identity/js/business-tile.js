(function($){

    if (undefined === $.identity) {
        $.identity = {};
    }

    $.identity.initialize_business_tiles = function() {
        $('[data-id=identityTile]').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

        }).each(function(i) {
            $(this).identity_action();
        });
    };

    $(function() {
        $.identity.initialize_business_tiles();
        $.navigation.reinitialize();
    });
})(jQuery);
