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
    
});
