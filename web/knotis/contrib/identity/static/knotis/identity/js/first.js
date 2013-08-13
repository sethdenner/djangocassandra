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

            $('#id-individual-form').ajaxform({
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

                },
                method: 'put'
            });

            $('#id-business-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        $('#first-carousel')
                            .carousel({interval: false})
                            .carousel('next');

                        $('#id-location-form #address-input #id_address').geocomplete({
                            map: '.map_canvas',
                            location: 'Seattle, WA, USA',
                            details: '#id-location-form',
                            detailsAttribute: 'data-geo'
                        });
                        
                        $('form#id-location-form input#related-id-input').val(
                            data.data.establishment_id
                        );

                        $('form#id-location-form').append(
                            '<input id="backend_name" type="hidden" value="' +
                            data.data.business_backend_name +
                            '"/>'
                        );

                    }

                }
            });

            $('#id-location-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        $('#modal-box').modal('hide');
                        var backend_name = $('form#id-location-form input#backend_name').val();
                        window.location = '/merchants/' + backend_name + '/';

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