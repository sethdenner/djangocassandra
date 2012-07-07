/*
 * render_data jQuery plugin
 * 
 * populate selected dom elements with data
 * 
 * supported sources should be ajax requests or data that has been provided in
 * the response from the sever (hidden field or something). this will take an
 * extra part to fetch the data.
 * 
 * data parameter should be in JSON format (maybe support other formats later
 * if it would be useful.
 * 
 * DOM elements look something like this:
 * 
 * <div id="user_template" data-resourceuri="RESOURCE_URI">
 *     <span class="name"></span>
 *     <span class="birthday"></span>
 *     <span class="status"></span>
 * </div>
 * 
 * when we make a call like:
 * 
 * $('#user_template').render_data(data);
 * 
 * it should iterate over all of the elements in data and generate markup for
 * them in-place (at the position of the template in the original markup).
 */

(function($) {
    var _options = null; //key/value collection of settings parsed from dom.
    
    var _get_data = function($template, attributes) {
        if (!attributes || !attributes.resource_uri) { return; } //ERROR.
        
        $.ajax({
            url: attributes.resource_uri,
            dataType: 'json',
            success: function(data, status, jq_xhr) {
                $template.attr({
                  'data-data': data      
                });
                $template.render_data();
            }
        });
    }
    
    var _get_attributes = function(element) {
        if (null === element) { return null; }
        
        attributes = new Object();
        element_attributes = element.attributes;
        attributes_length = element_attributes.length;
        for (var i = 0; i < attributes_length; ++i) {
            attribute = element_attributes.item(i);
            if (attribute.nodeName.indexOf('data-') != 0) { continue; }
            
            $.extend({
                attribute.nodeName: attribute:nodeValue
            }, attributes);
        }
        
        return attributes;
    }
    
    jQuery.fn.render_data = function(options) {
        _options = $.extend({
            'force_api': false //Forces data to be pulled from the API
        }, options);
        
        return this.each(function (){
            attributes = _get_attributes(this);

            if (null === attributes.data || true == _options.force_api) {
                _get_data(this, attributes);
                return true;
            }
            
            data = JSON.parse(attributes.data);
            
            $template = this;
            $.each(data, function(key, value){
                var $elements = $template.find('.' + key);
                $elements.each(function(){
                    $this = $(this);
                    if ($this.is('input')) {
                        $this.attr({
                            'name': key,
                            'value': value
                        });
                    } else {
                        $this.text(value);
                    }
                });
            });
        });
    };
})(jQuery);
