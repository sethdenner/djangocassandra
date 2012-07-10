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
    var DATA_PREFIX = 'data-';
    var _options = null; //key/value collection of settings parsed from dom.
    
    var _get_data = function($template, attributes) {
        if (!attributes || !attributes.resource_uri) { return; } //ERROR.
        
        $.ajax({
            url: attributes.resource_uri,
            dataType: 'json',
            success: function(data, status, jq_xhr) {
                var data_name = DATA_PREFIX + 'data';
                $template.attr({
                  data_name: data      
                });
                $template.render_data();
            }
        });
    };
    
    var _get_attributes = function(element) {
        if (null === element) { return null; }
        
        var attributes = {};
        var element_attributes = element.attributes;
        var attributes_length = element_attributes.length;
        for (var i = 0; i < attributes_length; ++i) {
            var attribute = element_attributes.item(i);
            var attribute_node_name = attribute.nodeName;
            if (attribute_node_name.indexOf(DATA_PREFIX) !== 0) { continue; }
            
            var name = attribute_node_name.substr(DATA_PREFIX.length);
            attributes = $.extend({
                name: attribute.nodeValue
            }, attributes);
        }
        
        return attributes;
    };
    
    jQuery.fn.render_data = function(options) {
        _options = $.extend({
            'force_api': false //Forces data to be pulled from the API
        }, options);
        
        return this.each(function (){
            var attributes = _get_attributes(this);

            if (null === attributes.data || true === _options.force_api) {
                _get_data(this, attributes);
                return true;
            }
            
            var data = JSON.parse(attributes.data);
            
            var $template = this;
            $.each(data, function(key, value){
                var $instance = $template.clone();
                var $elements = $instance.find('.' + key);
                $elements.each(function(){
                    var $this = $(this);
                    if ($this.is('input')) {
                        $this.attr({
                            'name': key,
                            'value': value
                        });
                    } else {
                        $this.text(value);
                    }
                });
                $template.after($instance);
            });
            $template.remove();
        });
    };
})(jQuery);
