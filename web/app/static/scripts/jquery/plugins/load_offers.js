(function($) {
    var _default_options = {
        'page_size': 20
    };
    var _options = _default_options;
    
    var _methods = {
        'init': function(options) {
            _options = $.extend(
                _default_options,
                options
            );
        },
        
        'load': function(
            callback,
            href,
            business,
            city,
            neighborhood,
            category,
            premium,
            page,
            query
        ){
            //Blow away old offers if offer source changes.
            var current_load_uri = this.attr('data-href');
            if (
                this.attr('data-href') != href ||
                this.attr('data-query') != query ||
                this.attr('data-business') != business ||
                this.attr('data-city') != city ||
                this.attr('data-neighborhood') != neighborhood ||
                this.attr('data-category') != category ||
                this.attr('data-premium') != premium
            ) {
                this.html('');
                page=1;       
            }
 
            //Make sure necessary attributes stay updated.
            this.attr('data-href', href)
                .attr('data-query', query)
                .attr('data-business', business)
                .attr('data-city', city)
                .attr('data-neighborhood', neighborhood)
                .attr('data-category', category)
                .attr('data-premium', premium)
                .attr('data-page', page);
            
            href = [
                href ? href.toLowerCase(): null,
                business ? business.toLowerCase() : null,
                city ? city.toLowerCase() : null,
                neighborhood ? neighborhood.toLowerCase() : null,
                category ? category.toLowerCase(): null,
                premium ? premium.toLowerCase() : null,
                page,
                ''
            ].join('/');
            
            var max = href.length;
            var cleaned_href = '';
            var last_char = null;
            var i = 0;
            for (i; i < max; ++i) {
                if (last_char == '/' && href[i] == last_char) {
                    continue;
                }
                
                last_char = href[i];
                cleaned_href += last_char;
            }
            
            var _data = 0;
            
            var request_data = {};
            
            if (query){
                request_data['query'] = query;
            }
            
            $.ajax(
                cleaned_href, {
                    'context': this,
                    'data': request_data,
                    'dataType': 'html'
                } 
            ).done(function(
                data, 
                status, 
                jqxhr
            ) {
                _data = $(data);

            }).fail(function(
                jqxhr,
                status,
                error
            ) {
                
            }).always(function(
                jqxhr,
                status
            ) {
                callback(
                    _data,
                    status,
                    jqxhr
                );
                
            });
        },
        
        'stop_scroll': function() {
            this.unbind('scroll.load_scroll');
        },
         
        'load_scroll': function(content_selector) {
            var throttled = false;
            
            this.unbind('scroll.load_scroll').bind(
                'scroll.load_scroll', 
                function(evt) {
                    if (throttled) { return; }
            
                    var $content = $(content_selector);
                    var $window = $(window);
                    var offers_bottom = ($content.offset().top + $content.height()) - 1000;
                    var window_bottom = $window.height() + $window.scrollTop();
            
                    if (offers_bottom < window_bottom) {
                        throttled = true;
                        
                        var href = $content.attr('data-href');
                        var business = $content.attr('data-business');
                        var city = $content.attr('data-city');
                        var neighborhood = $content.attr('data-neighborhood')
                        var category = $content.attr('data-category');
                        var premium = $content.attr('data-premium');
                        var query = $content.attr('data-query')
                        
                        var current_page = 0;
                        try {
                            current_page = parseInt($content.attr('data-page'));
                        } catch(exception) {}
                        
                        if (!href) { return; }
                        
                        rows = $content.children().children();
                        if (rows.length < _options.page_size * current_page) { return; }
                        
                        $content.load_offers(
                            'load', 
                            function(
                                data,
                                jqxhr,
                                status 
                            ) {
                                throttled = false;            
                                $content.append(data);
                            }, 
                            href,
                            business,
                            city,
                            neighborhood,
                            category,
                            premium,
                            current_page + 1,
                            query 
                        );
                    }
                }
            );
        }
    }
    
    $.fn.load_offers = function(method) {
        if (_methods[method]) {
            return _methods[method].apply(
                this, 
                Array.prototype.slice.call( 
                    arguments, 
                    1 
                )
            );
        } else if (typeof method === 'object' || ! method) {
            return _methods.init.apply( 
                this, 
                arguments 
            );
        } else {
            $.error('Method ' +  method + ' does not exist on jQuery.load_offers');
        }    
    };
})(jQuery);
/*
jQuery(function (){
    if ($('.offer-content').length) {
        $(document).load_offers(
            'load_scroll', 
            '.offer-content'
        );
    }
    
});
*/