;
(function($) {
    $(function(){
        FB.api('/me/accounts', function(response) {
            var $accounts = $('form#form-facebook-account-choice div#id-facebook-accounts');
            for (var i = 0; i < response.data.length; ++i) {
                var data = response.data[i];
                $accounts.append($(
                    '<div class="control-group"><div class="controls">' +
                    '<label><input name="facebook-account" type="radio" value="' + data.id +
                    '" />' + data.name + '</label></div></div>'
                ));
            }
        });

    });

})(jQuery);