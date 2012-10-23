/*****************************************************************************
 * Sickle jQuery Plugin
 * Copyright Knotis 2012
 * Author: Seth Denner
 * Date: 10/19/2012
 * 
 * This plugin uses this script to upload files: 
 * 
 *      https://github.com/valums/file-uploader
 * 
 * We also rely on shadowbox jQuery plugin to render the cropping window:
 * 
 *      http://www.shadowbox-js.com/
 * 
 * And then, of course, we use jCrop for the actual cropping functionality:
 * 
 *      https://github.com/tapmodo/Jcrop
 * 
 * Make sure these scripts are included on your page before Sickle jQuery.
 * 
 *****************************************************************************/
(function($) {
    var _options = null;
    
    $.fn.sickle = function(options) {
        _options = $.extend({
            action: '/media/ajax/',
            crop_form_url: '/image/crop/',
            params: {},
            close: function() {},
            done: function(data) {},
            fail: function(xhr, status) {},
            always: function(xhr, status) {},
            aspect: null
        }, options);
        
        return this.each(function() {
            id = $(this).attr('data-id')
            uploader = new qq.FileUploader({
                element: this,
                action: _options.action,
                debug: true,
                params: _options.params,
                onComplete: function(
                    id,
                    name,
                    response
                ){
                    $.colorbox({
                        href: [
                            _options.crop_form_url,
                            response.image_id,
                            '/'
                        ].join(''),
                        transition: 'fade',
                        scrolling: false,
                        overlayClose: false,
                        maxHeight: '100%',
                        maxWidth: '100%',
                        onClose: _options.close,
                        onComplete: function() {
                            $image = $('#sickle_image');
                            $image.Jcrop({
                                aspectRatio: _options.aspect,
                                onChange: function(coordinates) {
                                    $content = $('#sickle_content');
                                    $content.find('#id_crop_left').val(coordinates.x);
                                    $content.find('#id_crop_top').val(coordinates.y);
                                    $content.find('#id_crop_bottom').val(coordinates.y2);
                                    $content.find('#id_crop_right').val(coordinates.x2);
                                    $content.find('#id_crop_width').val(coordinates.w);
                                    $content.find('#id_crop_height').val(coordinates.h);
                                }
                            });
                            
                            $.colorbox.resize({
                                innerWidth: $image.width()
                            });
                            
                            $('#sickle_form').submit(function(event) {
                                $.ajax({
                                    url: $(this).attr('action'),
                                    type: 'POST',
                                    data: $(this).serialize(),
                                    dataType: 'json'
                                }).done(_options.done)
                                    .fail(_options.fail)
                                    .always(_options.always);
                                
                                event.preventDefault();
                                return false; 

                            });
                        
                        }
                        
                    })

                }
            });
            
        });
        
    };
    
})(jQuery);
