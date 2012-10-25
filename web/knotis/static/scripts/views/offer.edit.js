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
    var init_cropping = function() {
        $('.crop').sickle({
            aspect: 1,
            done: function(data) {
                if (data.status == 'success') {
                    $.get([
                        '/image/get_row/',
                        data.image_id,
                        '/'].join(''), function(data){
                        $('#image-list').html(data);
                        init_cropping();    
                    
                    })
                    
                } else if (data.status == 'failure') {
                    
                } else {
                    // Invalid Status
                }
            }
            
        });
        
    };
    init_cropping();

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
                    init_cropping();    
                
                })
                
            } else if (data.status == 'failure') {
                
            } else {
                // Invalid Status
            }
        }

    });

});
