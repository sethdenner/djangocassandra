$(function() {
    $('.delete_business_link').unbind('click').bind('click', function(evt) {
        var $this = $(this),
            href = $this.attr('href');
    
        $.post(
            href,
            {},
            function(data) {
                if (data != 'OK') { return; }
                
                $this.parent().remove();

            }
        );
    
        evt.stopPropagation();
        return false;
        
    });

});