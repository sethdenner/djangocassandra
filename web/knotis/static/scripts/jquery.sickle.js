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
            related_object_id: null,
            context: null,
            image_max_width: null,
            image_max_height: null,
            modal_selector: '#modal-box',
            jcrop_box_width: 0,
            jcrop_box_height: 0
        }, options);

        var _crop = function(image_id) {
            href = [
                _options.crop_form_url,
                image_id,
                '/',
                _options.related_object_id,
                '/',
                _options.context,
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

                var sx = 1.0, sy = 1.0;
                $image.load(function(){
                    var width = parseInt(this.width);
                    var height = parseInt(this.height);
                    var true_width = parseInt(this.naturalWidth);
                    var true_height = parseInt(this.naturalHeight);

                    sx = true_width/width;
                    sy = true_height/height;
                });

                var _update_coordinates = function(coordinates) {
                    var $content = $('#sickle_content');
                    $content.find('#id_crop_left').val(Math.round(sx * coordinates.x));
                    $content.find('#id_crop_top').val(Math.round(sy * coordinates.y));
                    $content.find('#id_crop_width').val(Math.round(sx * coordinates.w));
                    $content.find('#id_crop_height').val(Math.round(sy * coordinates.h));
                };

                default_box = [0, 0, _options.image_max_width, _options.image_max_height];
                $image.Jcrop({
                    aspectRatio: _options.aspect,
                    onChange: _update_coordinates,
                    onSelect: _update_coordinates,
                    setSelect: default_box,
                    boxWidth: _options.jcrop_box_width,
                    boxHeight: _options.jcrop_box_height
                });

                // Calculate this stuff after jcrop has loaded.

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
                '',
                function() {
                    $modal.on('shown', onComplete());
                    $modal.modal();
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
