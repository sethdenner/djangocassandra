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
        /**/
        window.location.getParameterByName = function(name) {
            name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
            var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
                results = regex.exec(location.search);
            return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
        }
        /**/

        if(!window.location.getParameterByName('redeem_query')) {
            $.paginator({
                url:window.location.pathname + 'grid',
                dataId:'id-redemptions',
                onDone: $.initializeRedemptionGrid
            });
        }
    });
})(jQuery);
