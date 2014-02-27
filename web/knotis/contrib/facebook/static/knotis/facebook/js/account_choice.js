;
(function($) {
    $(function(){
        FB.api('/me/accounts', function(response) {
            var $accounts = $('form#form-facebook-account-choice div#id-facebook-accounts');
            for (var i = 0; i < response.data.length; ++i) {
                var data = response.data[i];
                $accounts.append($(
                    '<div class="control-group"><div class="controls">' +
                    '<label><input name="account-id" type="radio" value="' + data.id +
                    '" data-account-name="' + data.name + '" data-access-token="' + data.access_token +
                    '" />' + data.name + '</label></div></div>'
                ));
            }
            $('input[name="account-id"]').click(function(event) {
                var $this = $(this);
                $('input[name="account-name"]').val($this.attr('data-account-name'));
                $('input[name="access-token"]').val($this.attr('data-access-token'));
            });

            $('#form-facebook-account-choice').ajaxform({
                done: function(data, staus, jqxhr) {
                    if (data.errors) {
                        var message = 'there was an error connecting your facebook account, please contact support';
                        alert('errors=TRUE');
                    } else {
                        $('div.social-integrations div.span12 div.row-fluid').append(
                            $(data.html)
                        );
                    }

                    $('#facebook-account-choice').modal('hide');
                }
            });
        });

    });

})(jQuery);