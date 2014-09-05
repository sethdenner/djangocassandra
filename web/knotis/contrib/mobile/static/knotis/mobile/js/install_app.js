(function ($) {
    if (undefined === $.knotis) {
        $.knotis = {};
    }

    $.knotis.detectAndroid = function () {
        if (!navigator.userAgent) {
            return false;

        }

        var userAgent = navigator.userAgent.toLowerCase()

        var androidRe = /.*android.*/;
        return androidRe.test(userAgent);

    };

    $.knotis.detectIOS = function () {
        if (!navigator.userAgent) {
            return false;

        }
        
        var userAgent = navigator.userAgent.toLowerCase()

        var iosRe = /.*ip(ad|hone).*/;
        return iosRe.test(userAgent);

    };

    $.knotis.installMobileApp = function () {
        var ios = $.knotis.detectIOS();
        var android = $.knotis.detectAndroid();

        if (ios) {
            alert('You are using iOS, Soon we will redirect you to install our app from the iTunes Store');

        } else if (android) {
            alert('You are using Android, Soon we will redirect you to install our app from Google Play');

        }

    };

})(jQuery);
