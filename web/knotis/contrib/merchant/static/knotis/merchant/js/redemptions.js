(function($) {
    $(function(){
        $('.redeem-offer').click(function(event) {
            event.stopPropagation();
            event.preventDefault();

            var $this = $(this);
            var transaction_id = $this.attr('data-transaction-id');

            $.post(
                '/my/redemptions/',
                {'transactionid': transaction_id},
                function(data, status, jqxhr) {
                    if (data.errors) {
                        alert(data.errors);
                    }
                    
                    $this
                        .parent()
                        .parent()
                        .parent()
                        .parent()
                        .hide('fast')
                        .remove();
                    
                }
            );
        });

    });
})(jQuery);