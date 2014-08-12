;
'use strict';

(function($){
    function initialized_purchase_tiles() {
        $('.offerItem').click(function(event) {
            event.preventDefault();
            event.stopPropagation();
        }).each(function(i) {
            var $this = $(this);
            var $action_button = $this.find('.print-voucher');
            $action_button.click(
                function(event){
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
    }
    $(function(){

        var page = 0;
        var count = 24;
        var auto_paging_cutoff = 3;
        var results_left = true;
        var fetching_results = false;
        var load_more_markup =  '<div class="row-fluid load-more">' +
            '<button class="btn btn-knotis-action btn-load-more">Load More Results</button>' +
            '</div>'
        var no_more_markup = '<div class="row-fluid load-more">' +
            '<button disabled class="btn btn-knotis-action btn-load-more">No More Results</button>' +
            '</div>'

        $(window).on('scroll.purchases', function(event) {

            var $this = $(this);

            $purchases = $('.contentBlock > .myPurchases')

            if (!$purchases.length || !results_left) {
                $this.off('scroll.purchases');
                return;
            }

            if (!fetching_results && $this.scrollTop() + $this.innerHeight() >= $(document).innerHeight() - 1000) {
                fetching_results = true;
                fetch_url = [
                        '/my/purchases/grid',
                        ++page,
                        count,
                        ''
                    ].join('/');
                $.get(
                    fetch_url,
                    function(data, status, request) {
                        data = data.replace(/(\r\n|\n|\r)/gm,"");
                        if (!data) {
                            results_left = false;
                            return;
                        }
                        var $markup = $(data);
                        $markup = $markup.children().children().children();
                        $('.span12 > .row-fluid').append($markup);
                        fetching_results = false;
                        initialized_purchase_tiles();
                    }
                );
            }
        });
        initialized_purchase_tiles();
    });
})(jQuery);
