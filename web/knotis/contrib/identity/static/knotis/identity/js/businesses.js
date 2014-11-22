(function($) {
    $(function(){
        $.paginator({
            url:'/businesses/grid',
            dataId:'id-establishments',
            onDone: $.identity.initializeBusinessTiles
        });
    });
})(jQuery);
