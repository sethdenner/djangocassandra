(function($) {
    var _options = null;
    
    var _methods = {
        'init': function(options) {
            
        },
        
        'load': function(
            callback,
            page,
            load_uri,
            context0,
            city,
            neighborhood,
            context1
        ){
            //Blow away old offers if offer source changes.
            var current_load_uri = this.attr('data-load_uri');
            if (
                this.attr('data-load_uri') != load_uri ||
                this.attr('data-context0') != context0 ||
                this.attr('data-city') != city ||
                this.attr('data-neighborhood') != neighborhood ||
                this.attr('data-context1') != context1
            ) {
                this.html('');                
            }
 
            //Make sure necessary attributes stay updated.
            this.attr('data-load_uri', load_uri)
                .attr('data-page', page)
                .attr('data-context0', context0)
                .attr('data-city', city)
                .attr('data-neighborhood', neighborhood)
                .attr('data-context1', context1);
            
            load_uri = [
                load_uri,
                context0,
                city,
                neighborhood,
                context1,
                page,
                ''
            ].join('/');
            
            var max = load_uri.length;
            var cleaned_uri = '';
            var last_char = null;
            for (var i = 0; i < max; ++i) {
                if (last_char == '/' && load_uri[i] == last_char) {
                    continue;
                }
                
                last_char = load_uri[i];
                cleaned_uri += last_char;
            }
            
            $.ajax(
                cleaned_uri, {
                    'context': this,
                } 
            ).done(function(
                data, 
                status, 
                jqxhr
            ) {
                this.append(data)

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
                    status,
                    jqxhr
                );
                
            });
        },
         
        'load_scroll': function(content_selector) {
            var throttled = false;
            
            this.unbind('scroll.load_offers').bind(
                'scroll.load_offers', 
                function(evt) {
                    if (throttled) { return; }
            
                    var $content = $(content_selector);
                    var $window = $(window);
                    var offers_bottom = ($content.offset().top + $content.height()) - 1000;
                    var window_bottom = $window.height() + $window.scrollTop();
            
                    if (offers_bottom < window_bottom) {
                        throttled = true;
                        
                        var load_uri = $content.attr('data-load_uri');
                        var uri_context0 = $content.attr('data-context0');
                        var city = $content.attr('data-city');
                        var neighborhood = $content.attr('data-neighborhood')
                        var context1 = $content.attr('data-context1');
                        var current_page = 0;
                        try {
                            current_page = parseInt($content.attr('data-page'));
                        } catch(exception) {}
                        
                        $content.load_offers(
                            'load', 
                            function(
                                jqxhr,
                                status 
                            ) {
                                $content.attr('data-page', current_page + 1)
                                $('.arrow').remove();

                                if ($content.find('.no-more-deals').length) {
                                    return;
                                }
                                
                                throttled = false;            
                                
                            }, 
                            current_page + 1, 
                            load_uri,
                            uri_context0,
                            city,
                            neighborhood,
                            context1
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
    
    $(document).load_offers(
        'load_scroll', 
        '.deal-content'
    );
    
})(jQuery);
