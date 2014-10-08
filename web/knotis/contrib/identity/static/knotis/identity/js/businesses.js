(function($) {
    $(function(){
        $.paginator({
            namespace:'scroll.businesses',
            url:'/businesses/grid',
            dataId:'id-establishments',
            onDone: $.identity.initializeBusinessTiles
        });
    });
})(jQuery);
