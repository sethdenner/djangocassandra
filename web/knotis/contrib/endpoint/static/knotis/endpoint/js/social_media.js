;
(function($) {
    $(function(){

        var required_permissions = ['publish_stream', 'manage_pages'];

        $('.disconnect').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            var $this = $(this);
            var endpoint_pk =  $this.attr('data-endpoint-pk');
            $.post(
                '/endpoint/delete/',
                {'endpoint_pk': endpoint_pk},
                function(data, status, jqxhr) {
                    if (data.errors) {
                        var message = data.errors['no-field'];
                        alert(message);
                    } else {
                        $('a.disconnect[data-endpoint-pk="' + endpoint_pk + '"]')
                            .parent().parent().remove();
                    }
                }
            );

        });

        $('.connect-facebook').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            var fb_login = function(response) {
                FB.login(function(response) {
                    if (response.authResponse) {
                        handle_connected(response);
                    } else {
                        console.log('User cancelled login or did not fully authorize.');
                    }
                }, {
                    scope: required_permissions.join(','),
                    enable_profile_selector: true
                });
            };

            var handle_connected = function(response) {
                console.log('Welcome!  Fetching your information.... ');
                console.log('Access Token: ' + response.authResponse.accessToken);
                FB.api('/me', function(response) {
                    console.log('Good to see you, ' + response.name + '.');
                    FB.api('/' + response.id + '/permissions', function(response) {
                        console.log('Your permissions are:')
                        var missing_permissions = false;
                        var permissions = []
                        for (var i = 0; i < response.data.length; ++i) {
                            for (var key in response.data[i]) {
                                console.log('\t' + key);
                                if (1 === response.data[i][key]) {
                                    permissions.push(key);
                                }
                            }
                        }
                        for (var i = 0; i < required_permissions.length; ++i){
                            if (-1 === permissions.indexOf(required_permissions[i])) {
                                missing_permissions = true;
                                break;
                            }
                        }

                        if (missing_permissions) {
                            fb_login();
                            return;
                        }

                        $.ajaxmodal({
                            href: '/facebook/choose-account/',
                            modal_id: 'facebook-account-choice',
                        });
                        
                    });
                });
            };

            FB.getLoginStatus(function(response) {
                if (response.status === 'connected') {
                    handle_connected(response);
                } else{
                    fb_login();
                }
            });
        });

        $('.connect-twitter').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            $.get(
                '/twitter/authorize/',
                '',
                function(data, status, jqxhr) {
                    var authorize_url = data.authorize_url;
                    var oauth_token = data.oauth_token;
                    var oauth_token_secret = data.oauth_token_secret;

                    window.open(
                        authorize_url,
                        '',
                        'width=640,height=480,menubar=no,titlebar=no,toolbar=no'
                    )

                    $.ajaxmodal({
                        href: '/twitter/verify-pin',
                        modal_id: 'twitter-verify-pin',
                        on_open: function(data, status, request) {
                            $('a#a-authorize').attr('href', authorize_url);
                            $('input#oauth_token').val(oauth_token);
                            $('input#oauth_token_secret').val(oauth_token_secret);
                        }
                    });
                }
            );

        });

    });
})(jQuery);