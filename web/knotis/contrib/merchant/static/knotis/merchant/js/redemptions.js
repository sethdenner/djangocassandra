(function($) {
    $.initializeRedemptionGrid = function() {
        $('[data-id=id-redeem]').off('click.redeem').on('click.redeem', function(event) {
            event.stopPropagation();
            event.preventDefault();

            var $this = $(this);
            var transaction_id = $this.attr('data-transaction-id');

            $.post(
                '/my/redemptions/',
                {'transaction_id': transaction_id},
                function(data, status, jqxhr) {
                    if (data.errors) {
                        alert(data.errors);
                    }

                    $this
                        .parent()
                        .parent()
                        .parent()
                        .parent()
                        .hide('slow')
                        .remove();
                }
            );
        });
    }
    $(function(){

        $.initializeRedemptionGrid();

        $.paginator({
            namespace:'scroll.redemptions',
            url:window.location.pathname + 'grid',
            dataId:'id-redemptions',
            onDone: $.initializeRedemptionGrid
        });

    });
})(jQuery);
