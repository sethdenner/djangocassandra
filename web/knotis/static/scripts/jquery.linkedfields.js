(function($){
	
	/**
		$.link_field
		declares an element to be a link_field, which updates all other
		like link_fields and is updated by all other like link_fields.
		
		@param group: all link_fields with the same group field will 
		update to the same value returned by getAttr, as long as the 
		change event passes this customFilter and their update 
		functions.
		
		@param update: a function that handles updating this element.
		
		@param get_val: a function returning this element's value to be
		synced to other link_fields in the same group.
		
		Adds a `link_field` class and a `data-link-group` attribute. 
		
		Default behavior after a group has been defined is to attach a 
		change handler which will let the plugin react to every input
		event with a call to its privatish method _update_others, 
		(calling update once for each other element in the same group, 
		and taking care to temporarily detach their input handlers so 
		as to prevent a cascading chain reaction of doom.) This plugin 
		hands the _update_others function the value returned by this
		elements' get_val(). 
	*/
	$.fn.link_field = function(group, update, get_val){
		
		$(this).each(function(){	
		
			if(!group){
				return this;
			}
			
			var self = this;
			
			this._update_others = (function(){
				return function(val){
					var o = $('[data-link-group=' + group + ']').not(self);
					o.each(function(){
						this.update(val);
					});
				
					return o;
				};
			})();

			this.group = group;
			this.update = update || function(val){
				if($(self).is('input')){
					$(self).val(val);
				}else{
					$(self).text(val);
				}
			};
			this.get_val = get_val || function(){
				if($(self).is('input')){
					return $(self).val();
				}else{
					return $(self).text();
				}
			};
			
			$(this).addClass('link-field');
			$(this).attr('data-link-group', group);
			
			this.sync = function(){
				self._update_others(self.get_val());
			}
			
			this.addEventListener('input', this.sync);
			
			return this;
		
		});
	};
	
})(jQuery);
