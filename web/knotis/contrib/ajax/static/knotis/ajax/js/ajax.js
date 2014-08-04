;

(function ($) {
    'use strict';

    var default_settings = {
        callback: function () {}
    };

    var Loading = function (settings) {
        this.init(settings);

    };

    Loading.prototype.init = function (settings) {
        this.settings = $.extend(default_settings, settings);

    };

    Loading.prototype.on = function () {
        $('#id-loading').removeClass('hide');
        if (this.settings.callback) {
            this.settings.callback();

        }

    };

    Loading.prototype.off = function () {
        $('#id-loading').addClass('hide');
        if (this.settings.callback) {
            this.settings.callback();

        }

    };

    Loading.prototype.toggle = function () {
        $('#id-loading').toggleClass('hide');
        if (this.settings.callback) {
            this.settings.callback();

        }

    };

    $.loading = function (method, settings) {
        var loading = new Loading(settings);
        return loading[method]();

    };

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    }

    $.ajaxSetup({
        crossDomain: false // obviates need for sameOrigin test
    });

    var $document = $(document);
    $document.ajaxStart(function () {
        $.loading('on');

    }).ajaxSend(function (event, xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader(
                "X-CSRFToken",
                $.cookie('csrftoken')
            );

        }

    }).ajaxComplete(function () {
        $.loading('off')

    });

})(jQuery);