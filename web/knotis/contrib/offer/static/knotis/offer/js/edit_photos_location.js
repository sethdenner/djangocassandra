(function($){
    $(function(){
        $('#add_offer_photo').click(function(event){
            event.preventDefault();
            event.stopPropagation();

            offer_id = $('#offer_photo_location_form #id_offer').val();

            var modal_id = 'offer-add-image';

            $.ajaxmodal({
                href: '/image/upload',
                modal_settings: {
                    backdrop: 'static'
                },
                modal_id: modal_id,
                on_open: function(data, status, request) {
                    $('#file-uploader').sickle({
                        do_upload: true,
                        params: {
                            type: 'image',
                        },
                        aspect: 240/135,
                        modal_selector: '#' + modal_id,
                        done: function(data) {
                            if (data.status == 'success') {
                                var item_row_template = [
                                    '<div class="control-group">',
                                    '<input checked type="radio" name="photo" value="{{image_id}}">&nbsp;',
                                    '<img style="width: 32px; height: 21px;" src="{{image_src}}">&nbsp;',
                                    '<a data-method="GET" class="item-action " href="#">Crop</a>',
                                    '&nbsp;&nbsp;|&nbsp;&nbsp;',
                                    '<a data-method="DELETE" class="item-action " href="#">Delete</a>',
                                    '</div>'
                                ].join('');
                                var item_row = item_row_template
                                    .replace('{{image_id}}', data.image_id)
                                    .replace('{{image_src}}', data.image_url);
                                var $item_row = $(item_row);
                                $('form#offer_photo_location_form #photos .controls:first').append($item_row)
                                    .stop().animate({
                                        scrollTop: $item_row.offset().top
                                    }, 500);
                                

                            } else if (data.status == 'failure') {
                                
                            } else {
                                // Invalid Status
                            }
                        },
                        related_object_id: offer_id,
                        context: 'offer_banner'
                    });
                }
            });
            
        });
    });
})(jQuery);