(function($) {
    $(function () {
        

        $('#wtb-button').click(function(event){
            event.preventDefault();
            
            $.ajaxmodal({
                href: '/where-to-buy/'
            });
        });

    });
})(jQuery);
