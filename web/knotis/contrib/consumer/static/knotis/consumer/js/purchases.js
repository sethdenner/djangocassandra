;
'use strict';

(function($){
    $(function(){
        $.paginator({
            url:window.location.pathname + 'grid',
            dataId:'id-purchases',
            count_increment: 50
        });
    });
})(jQuery);
