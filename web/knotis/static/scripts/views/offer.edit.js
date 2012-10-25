$(function() {
    $('#check_unlimited').change(function(event) {
        if (this.checked) {
            $('#stock')
                .val('')
                .attr('disabled', 'disabled')
                .attr('placeholder', 'Unlimited');
            
        } else {
            $('#stock')
                .removeAttr('disabled')
                .attr('placeholder', 'Units');
            
        }
    });

    offer_id = $('#update_offer').attr('data-id');
    var init_file_uploader = function() {
        $('#file-uploader').sickle({
            do_upload: true,
            params: {
                id: offer_id ? offer_id : null,
                type: 'image'
            },
            aspect: 1,
            done: function(data) {
                if (data.status == 'success') {
                    $('#image-id').val(data.image_id);
                    $.get([
                        '/image/get_row/',
                        data.image_id,
                        '/'].join(''), function(data){
                        $('#image-list').html(data);
                        init_image_list();    
                    
                    })
                    
                } else if (data.status == 'failure') {
                    
                } else {
                    // Invalid Status
                }
            }
    
        });
    };
    init_file_uploader();
    
    var init_image_list = function() {
        $('.crop').sickle({
            aspect: 1,
            done: function(data) {
                if (data.status == 'success') {
                    $.get([
                        '/image/get_row/',
                        data.image_id,
                        '/'].join(''), function(data){
                        $('#image-list').html(data);
                        init_image_list();    
                    
                    })
                    
                } else if (data.status == 'failure') {
                    
                } else {
                    // Invalid Status
                }
            }
            
        });
        
        $('.delete-image').unbind('click').bind('click', function() {
            var $this = $(this),
                    image_id = $this.attr('data-image-id'),
                    business_id = $this.attr('data-business-id');
    
            $.post([
                '/image/delete',
                image_id,
                ''].join('/'), 
                {},
                function(data) {
                    if (data != 'OK') { return; }
                        $('#image-list').html('<div id="file-uploader"></div><div class="clean"></div>');                        
                        init_file_uploader();    
                    });
    
            return false;
    
        });
        
    };
    init_image_list();

});
