(function($) {

    var print_recurse = function(obj, target, prefix){};

    // ********** DECORATORS GO HERE ********** //
    function value_handler(obj, target, prefix){
        target.append('<p>' + prefix + ':' + obj.data + '</p>');
    }

    function list_handler(obj, target, prefix){
        $.each(obj.data, function(key, thing){
            print_recurse(thing, target, '');
        });
    }

    function dict_handler(obj, target, prefix){
        // Print local values before recursing.
        // Can be changed to have other prefential processing.
        $.each(obj.data, function(key, thing){
            if ('value' === thing.type){
                print_recurse(thing, target, key);
            }
        });
        $.each(obj.data, function(key, thing){
            if (!('value' === thing.type)){
                print_recurse(thing, target, key);
            }
        });
    }

    function form_handler(obj, target, prefix){
        form_string = '';
        form_string += '<form ';
        form_string +=   'action="' + obj.action + '" ';
        form_string +=   'id="' + obj.id + '" ';
        form_string +=   'method="' + obj.method + '" ';
        form_string += '>';
        form_string += '</form>';
        target.append(form_string);
        var form_target = $('#' + obj.id);
        $.each(obj.data, function(key, thing){
            print_recurse(thing, form_target, key);
        });
        $(form_target).append('<input type="submit" value="' + obj.button + '">');
        $(form_target).ajaxform({
        //  done: FIX ME LATER TO DISPLAY STATUS
        });
    }

    function field_handler(obj, target, prefix){
        field_string = '';
        if (!('hidden' === obj.ftype)){
            field_string += obj.fname.toUpperCase() + ':&nbsp;';
        }
        field_string += '<input ';
        field_string +=   'name="' + obj.fname + '" ';
        field_string +=   'type="' + obj.ftype + '" ';
        field_string +=   'value="' + obj.data + '" ';
        field_string += '>'
        target.append(field_string);
    }





    // ********** RECURSIVE PRINT ********** //
    print_recurse = function(obj, target, prefix){
        switch (obj.type) {
            case 'value':
                value_handler(obj, target, prefix);
                break;
            case 'list':
                list_handler(obj, target, prefix);
                break;
            case 'dict':
                dict_handler(obj, target, prefix);
                break;
            case 'form':
                form_handler(obj, target, prefix);
                break;
            case 'field':
                field_handler(obj, target, prefix);
                break;
            default:
                break;
        }
    }




    // ********** FORM BUILDING ********** //

    $('#admin_query_form').ajaxform({
        done: function(query_response, status, jqxhr) {
            $('.admin_list_entry').remove();
            var result_target = $('#admin_list_results');
            $.each(query_response.results, function(key, thing){
                var entry_string = '';
                entry_string += '<div class="admin_list_entry" id="admin_list_entry_'
                              +     key
                              + '">'
                              +    '<div class="admin_list_tag">'
                              +        key
                              +    '</div>'
                              +    '<div id="admin_list_value_'
                              +        key
                              +    '">'
                              +    '</div>'
                              +'</div>'
                result_target.append(entry_string);
                var target = $('#admin_list_value_' + key);
                print_recurse(thing, target, '');
            });
        }
    });
    $('#admin_create_form').ajaxform({
    //  done: FIX ME LATER TO DISPLAY STATUS
    });
})(jQuery);
