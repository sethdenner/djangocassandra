(function($) {
    
    $('#modal-box').modal({
        backdrop: 'static',
        keyboard: false,
    });

    $.get(
        '/identity/first/',
        {},
        function(data, status, jqxhr) {
            $('#modal-box').html(data);
        }
    );

})(jQuery);