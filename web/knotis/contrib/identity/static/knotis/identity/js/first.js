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

            $('#id-identity-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        $('#first-carousel')
                            .carousel({interval: false})
                            .carousel('next');

                        $('#modal-box').modal({
                            backdrop: true,
                            keyboard: true
                        });

                    }

                }
            });

            $('#first-carousel button#id-button-business').click(function(event) {
                event.preventDefault();
                $('#first-carousel').carousel('next');
                
            });

            $('#first-carousel button#id-button-offers').click(function(event) {
                event.preventDefault();
                $('#modal-box').modal('hide');

            });

        }

    );

})(jQuery);