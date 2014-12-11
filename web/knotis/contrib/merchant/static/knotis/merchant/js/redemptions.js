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
                onDone: $.initializeRedemptionGrid,
                count_increment: 50
            });
        }

        $('[data-id=redeem-query]').keyup(function(event) {
            key_press = String.fromCharCode(event.keyCode)
            var query = $.trim($(this).val());
            var regx = /^[A-Za-z0-9]+$/;
            if (regx.test(key_press) && regx.test(query) && query.length >= 3) {
                $.ajax({
                    url: window.location.pathname + 'grid/' + '?redeem_query=' + query,
                    success: function(data, status, request) {
                        data = data.replace(/(\r\n|\n|\r)/gm,"");
                        var $markup = $(data);

                        $('div[data-id=id-redemptions]').replaceWith($markup);

                        $.initializeRedemptionGrid();
                        $.navigation.reinitialize();
                        $(window).off('scroll');
                    }
                });
            }
        });
    });
})(jQuery);
