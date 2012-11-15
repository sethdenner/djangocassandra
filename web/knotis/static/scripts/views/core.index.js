$(function(){
    (function(){
        $('.content-home').load_offers({
            'page_size': 12,
            'items_per_row': 3
        });

        $(document).load_offers(
            'load_scroll', 
            '.content-home'
        );
        
    })();

});
