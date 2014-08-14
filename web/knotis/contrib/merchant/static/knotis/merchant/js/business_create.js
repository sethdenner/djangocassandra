(function($) {
    $('#id-business-form').ajaxform({
        done: function(data, status, jqxhr) {
            if (data.errors) {
                alert('There was an error creating your business.');
                return;
            }

            $.get(
                '/identity/switcher/',
                'format=json',
                function (data) {
                    if (data.errors || !data.html) {
                        alert('No id switcher :(');
                        return;
                    }

                    $('#identity-switcher').replaceWith(data.html);
                }
            );

            $('#business-create').modal('hide');
            window.location = '/';
        }
    });

})(jQuery);
