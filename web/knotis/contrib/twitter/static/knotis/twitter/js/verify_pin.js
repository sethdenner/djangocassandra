;
(function($) {
    $(function(){
        $('form#form-twitter-verify-pin').ajaxform({
            done: function(data, staus, jqxhr) {
                if (data.errors) {
                    var message = 'there was an error connecting your twitter account, please contact support';
                    alert('errors=TRUE');

                } else {
                    $('div.social-integrations div.span12 div.row-fluid').append(
                        $(data.html)
                    );

                }

                $('#twitter-verify-pin').modal('hide');
            }
        });

    });
})(jQuery);