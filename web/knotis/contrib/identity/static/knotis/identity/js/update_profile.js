(function($){
/*
    $('#modal-box').modal({
	backdrop: 'static',
	keyboard: false
    });
*/

    var $updateable_addresses = $('.update-address-link');

    if($updateable_addresses){

	var update_address = function(){
	    var $this = $(this);
	    $.get(
		'/location_form/',
		{},
		function(data, status, jqxhr){
		    // fill the modal
		    $('#modal-box').modal({
			backdrop: 'static',
			keyboard: false,
		    });
		    
		    $('#modal-box').html(data);

		    // submit form and close modal, when done
		    $('#id-location-form').ajaxform({
			done: function(data, status, jqxhr){
			    if(!data.errors){
				$this.text($('#id_address').val());
				$('#modal-box').modal('hide');
			    }else{
				console.log(data.errors);
			    }
			},
			method: 'post'
		    });

		    $('#modal-box').modal();
		    
		    $('#id-location-form #address-input #id_address').geocomplete({
			map: '.map_canvas',
			location: $this.text(),
			details: '#id-location-form',
			detailsAttribute: 'data-geo'
		    });

		});
	};

	$updateable_addresses.on('click', update_address);
    }

})(jQuery);
