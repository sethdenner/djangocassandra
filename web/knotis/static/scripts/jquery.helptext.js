// TODO: Write Documentation
//
//
//
//
(function($) {
    $.fn.helptext = function(options) {
        
        var settings = $.extend({
            version: '0'
        }, options);
        
        var helpTextHtml = '<div class="help-text hide"><div class="help-text-internal"><h5></h5><p></p></div></div>';
        return this.each(function(){
            $(this).unbind('mouseenter mouseleave').hover(function(event){
                var $this = $(this);
                var id = $this.attr('id');
                var id = id.replace(/^ht-/, '');
                $.ajax({
                    url: '/static/scripts/helptext.json?' + settings.version,
                    cache: true,
                    dataType: 'json',
                    error: function(jqXHR, textStatus, errorThrown) {
                        //No text, do nothing?
                        alert('Error getting helptext.json: ' + textStatus);
                    },
                    success: function(data, textStatus, jqXHR) {
                        var helpTextObj = data['en-us'][id];
                        var $helpTextBox = $('.help-text');
                       
                        //Generate new box if it doesn't exist.
                        if (0 == $helpTextBox.length) {
                            $helpTextBox = $(helpTextHtml);
                            $helpTextBox.bind('mouseleave', function(event){
                               $(this).hide(); 
                            });
                            $helpTextBox.appendTo($('body'));
                        }
                        
                        $helpTextBox.children().children('h5').html(helpTextObj.title);
                        $helpTextBox.children().children('p').html(helpTextObj.text);
                        
                        var offset = $this.offset();
                        
                        var scrollAdjustedOffset = {
                                top: offset.top - $(window).scrollTop(),
                                left: offset.left - $(window).scrollLeft()
                        }
                        
                        //Handle box off bottom of window.
                        if (scrollAdjustedOffset.top + $helpTextBox.outerHeight() > $(window).height()) {
                            offset.top -= $helpTextBox.outerHeight() - $this.outerHeight();
                        }   
                        
                        //Handle box off right of window.
                        if (scrollAdjustedOffset.left + $helpTextBox.outerWidth() > $(window).width()) {
                            offset.left -= ($helpTextBox.outerWidth());
                        } else {
                            offset.left += $this.outerWidth();
                        }
                        
                        $helpTextBox.css('top', offset.top).css('left', offset.left);

                        $helpTextBox.show();
                    }
                });
            },
            function(event){
                var $helpTextBox = $('.help-text');
                if (!$helpTextBox.is(':visible')) { return; }
                
                var mouseX = event.pageX;
                var mouseY = event.pageY;
                var boxOffset = $helpTextBox.offset();
                var boxWidth = $helpTextBox.width();
                var boxHeight = $helpTextBox.height();
                if (mouseX > boxOffset.left && 
                    mouseX < (boxOffset.left + boxWidth) &&
                    mouseY > boxOffset.top &&
                    mouseY < (boxOffset.top + boxHeight)) {
                    return;
                }
                    
                $('.help-text').hide();
            });
        });
    };
    
    //Run when ajax requests complete.
    $(document).ajaxComplete(function(event, XMLHttpRequest, ajaxOptions) {
        $('.help-icon').helptext();
    });
    
    //Run Automatically
    $(document).ready(function(){
        $('.help-icon').helptext();
    });
}(jQuery));
