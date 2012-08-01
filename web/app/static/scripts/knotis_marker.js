var KnotisMarker = function(options) {

    if (options.profile == '0') {

        this._div = $('<div class="push radius-general relative"><div class="push-category absolute push-' + options.icon_var + '"></div><img class="thumb" alt="' + options.title_var + '" src="' + options.icon + '"></div>');
        this._popup = $('<div class="push-info radius-general"> <p><a href="' + options.url_var + '">' + options.title_var + '</a></p><p>' + options.description_var + '</p></div>');
    }

    if (options.profile == '1') {
        this._div = $('<div class="push-general"></div>');
        this._popup = $('');
    }

    this._div.append(this._popup);

    this._latlng = options.position;

    this.setMap(options.map);

    this._div.hover($.proxy(this.openPopup, this), $.proxy(this.closePopup, this));

    google.maps.event.addDomListener(this._div, 'mousedown', KnotisMarker.cancelEvent);
    google.maps.event.addDomListener(this._div, 'dblclick', KnotisMarker.cancelEvent);
};

KnotisMarker.prototype = new google.maps.OverlayView();

KnotisMarker.prototype.onAdd = function() {
    this.getPanes().overlayImage.appendChild(this._div.get(0));
};

KnotisMarker.prototype.onRemove = function() {
    if (this._div && this._div.parentNode) {
        this._div.parentNode.removeChild(this._div.get(0));
        this._div = null;
    }
};

KnotisMarker.prototype.draw = function() {
    // Get the point on the map in pixels
    var p = this.getProjection().fromLatLngToDivPixel(this._latlng),
            x = 0,
            y = 0;

    // Now position our div
    // Take into account the center of the marker
    x = Math.ceil(p.x - this._div.width() / 2);
    y = Math.ceil(p.y - this._div.height() / 2);

    this._div.css({left: x + "px", top: y + "px"});

};

KnotisMarker.prototype.openPopup = function() {
    this._popup.show();
};

KnotisMarker.prototype.closePopup = function() {
    this._popup.hide();
};

KnotisMarker.prototype.getPosition = function() {
    return this._latlng;
};

KnotisMarker.cancelEvent = function(e) {
    e.cancelBubble = true;
    if (e.stopPropagation) e.stopPropagation();
};

