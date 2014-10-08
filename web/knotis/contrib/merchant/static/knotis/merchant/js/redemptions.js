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

                    $('[data-redemption-tile-id=' + transaction_id + ']').hide(
                        'slow',
                        function () {
                            $(this).remove();
                        }
                    );
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
