;
'use strict';

(function($){
    $(function(){
        $.paginator({
            url:window.location.pathname + 'grid',
            dataId:'id-purchases',
        });
    });
})(jQuery);
