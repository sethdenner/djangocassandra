;
'use strict';

(function($){
    $(function(){
        $('button.action.print-voucher').click(function(event){
            event.preventDefault();
            event.stopPropagation();
            
            var $this = $(this);
            var transaction_id = $this.attr('data-transaction-id');

            window.open([
                '/my/purchases',
                transaction_id,
                'printable',
                ''
            ].join('/'));
        });
    });
})(jQuery);