(function($) {
    
    $('.tile-create').click(function(event){
        event.preventDefault();

        var $this = $(this);
        var create_action = $this.attr('data-create-action');
        var action_type = $this.attr('data-action-type');

        if (action_type == 'redirect') {
            window.location = create_action;
            return false;

        }
        
        if (action_type == 'modal') {
            $('#modal-box').modal({
                backdrop: 'static',
                keyboard: true
            });

            $.get(
                create_action,
                {},
                function(data, status, jqxhr) {
                    $('#modal-box').html(data);
                    
                }
            );
        }    
    });

})(jQuery);