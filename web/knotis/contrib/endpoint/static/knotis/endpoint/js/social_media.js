;
(function($) {
    $(function(){
        
        $('.connect-facebook').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            FB.getLoginStatus(function(response) {
                if (response.status === 'connected') {
                    console.log('Welcome!  Fetching your information.... ');
                    console.log('Access Token: ' + response.authResponse.accessToken);
                    FB.api('/me', function(response) {
                        console.log('Good to see you, ' + response.name + '.');
                        FB.api('/' + response.id + '/permissions', function(response) {
                            console.log('Your permissions are:')
                            for (var i = 0; i < response.data.length; ++i) {
                                for (var key in response.data[i]) {
                                    console.log('\t' + key);
                                }
                            }
                        });
                    });
                    
                } else{
                    FB.login(function(response) {
                        if (response.authResponse) {
                            console.log('Welcome!  Fetching your information.... ');
                            console.log('Access Token: ' + response.authResponse.accessToken);
                            FB.api('/me', function(response) {
                                console.log('Good to see you, ' + response.name + '.');
                            });
                        } else {
                            console.log('User cancelled login or did not fully authorize.');
                        }
                    }, {
                        scope: 'publish_stream,manage_pages,publish_actions',
                        enable_profile_selector: true
                    });
                }
            });
        });

    });
})(jQuery);