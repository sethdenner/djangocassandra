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
 * We also rely on bootstrap-modal to render the cropping window:
 * 
 *      https://github.com/jschr/bootstrap-modal
 * 
 * And then, of course, we use jCrop for the actual cropping functionality:
 * 
 *      https://github.com/tapmodo/Jcrop
 * 
 * And the knotis fork of sorl-thumbnail to serve the cropped images:
 * 
 *      https://github.com/knotis/sorl-thumbnail
 * 
 * Make sure these scripts are included on your page before Sickle jQuery.
 * 
 *****************************************************************************/
(function($) {
    var _options = null;
    
    $.fn.sickle = function(options) {
        var _options = $.extend({
            action: '/image/ajax/',
            crop_form_url: '/image/crop/',
            params: {},
            close: function() {},
            done: function(data) {},
            fail: function(xhr, status) {},
            always: function(xhr, status) {},
            aspect: null,
            image_id: null,
            image_max_width: null,
            image_max_height: null,
            modal_selector: '#modal-box'
        }, options);
        
        var _crop = function(image_id) {
            href = [
                _options.crop_form_url,
                image_id,
                '/'
            ].join('');
            if (_options.image_max_width && _options.image_max_height) {
                href = [
                    href,
                    _options.image_max_width,
                    '/',
                    _options.image_max_height,
                    '/'
                ].join('');
            }
            
            var $modal = $(_options.modal_selector);
            var onComplete = function() {
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
                
                $('#sickle_form').submit(function(event) {
                    $.ajax({
                        url: $(this).attr('action'),
                        type: 'POST',
                        data: $(this).serialize(),
                        dataType: 'json'
                    }).done(function(data) {
                        $modal.modal('hide');
                        _options.done(data);
                        
                    }).fail(_options.fail)
                        .always(_options.always);
                    
                    event.preventDefault();
                    return false; 

                });
                
            };

            $modal.load(
                href,
                {},
                function() {
                    $modal.modal();
                    onComplete();
                }
            );

        };
        
        return this.each(function() {
            if (true == _options.do_upload) {
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
                        _crop(response.image_id);
                    }
                });
                
             } else {
                 $(this).unbind('click.sickle').bind('click.sickle', function(event){
                     _crop($(this).attr('data-image-id'));
                    
                    event.stopPropagation();
                    return false;
                                         
                 });
                 
             }
            
        });
        
    };
    
})(jQuery);
