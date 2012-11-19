$(function(){
    (function(){
        $('.content-home').load_offers({
            'page_size': 12,
            'items_per_row': 3
        });

        var load_count, load_max = 4;
        var load_scroll = function() {
            load_count = 0;
            $(document).load_offers(
                'load_scroll', 
                '.content-home',
                function(
                    data,
                    jqxhr,
                    status
                ) {
                    ++load_count;
                    if (load_count >= load_max) {
                        $(document).load_offers(
                            'stop_scroll'
                        );

                    }
                }
            );
        };
        load_scroll();
        
        $('.load_more_results').click(function(evt){
            if (load_count >= load_max){
                $content = $('.content-home'); 
                $content.load_offers(
                    'load',
                    function(
                        data,
                        jqxhr,
                        status
                    ) {
                        $content.append(data);
                        load_scroll();               
                        
                    },
                    $content.attr('data-href'),
                    $content.attr('data-business'),
                    $content.attr('data-city'),
                    $content.attr('data-neighboorhood'),
                    $content.attr('data-category'),
                    $content.attr('data-premium'),
                    (parseInt($content.attr('data-page')) + 1).toString(),
                    $content.attr('data-query')
                )

            }
            evt.stopPropagation();
            return false;
            
        });
        
    })();

});
