;
'use strict';

(function($){
    $(function(){
        $.paginator({
            namespace:'scroll.purchases',
            url:window.location.pathname + 'grid',
            dataId:'id-purchases',
        });
    });
})(jQuery);
