(function($){

    if (undefined === $.identity) {
        $.identity = {};
    }

    $.identity.initializeBusinessTiles = function() {
        $('[data-id=identityTile]').click(function(event) {

        }).each(function(i) {
            $(this).identity_action();
        });
    };

    $(function() {
        $.identity.initializeBusinessTiles();
        $.navigation.reinitialize();
    });
})(jQuery);
