(function($) {
    $('#admin_list_controls').ajaxform({
        done: function(data, status, jqxhr) {
            $('.admin_list_entry').remove();
            var user_results = $('#admin_list_results');
            $.each(data.users, function(ukey, uvalue) {
                var pos_num = ukey + data.start;
                var user_tag = 'user_' + uvalue.id;
                var user_entry = '<div class="admin_list_entry" '
                               +     'id="' + user_tag +'"'
                               + '>'
                               +     '<div class="admin_list_tag">'
                               +     pos_num
                               +     '</div>'
                               +     '<div class="admin_list_value">'
                               +         '<div> ID: ' + uvalue.id + '</div>'
                               +         '<form '
                               +             'action="/admin/user/interact/update-' + uvalue.id + '/" '
                               +             'id="' + user_tag + '_form" '
                               +             'method="post"'
                               +         '>'
                               +             'USERNAME: <input name="username" type="text" id="' + user_tag + '_username" '
                               +                 'value="' + uvalue.username + '"'
                               +             '>'
                               +             '<input type="submit" value="Save" id="' + user_tag + '_button">'
                               +         '</form>'
                               +     '</div>'
                               + '</div>'
                user_results.append(user_entry);
                $('#' + user_tag + '_form').ajaxform({
//                    done: FIX ME LATER TO DISPLAY STATUS
                });
                user_entry = $('#' + user_tag);
                $.each(uvalue.identities, function(ikey, ivalue){
                    var id_tag = 'ident_' + ivalue.id;
                    var id_entry = '<div id="' + id_tag + '">'
                                 + '<div> IDENTITY: ' + ivalue.id + '</div>'
                                 + '<div> NAME: ' + ivalue.name + '</div>'
                                 + '<div> TYPE: ' + ivalue.type + '</div>'
                    user_entry.append(id_entry);
                    id_entry = $('#' + id_tag);
                    $.each(ivalue.endpoints, function(ekey, evalue){
                        var ep_tag = 'end_' + evalue.id;
                        var ep_entry = '<div id="' + ep_tag + '">'
                                     +     '<form '
                                     +         'action ="../../api/v0/endpoint/"'
                                     +         'id="' + ep_tag + '_form" '
                                     +         'method="post"'
                                     +     '>'
                                     +         'ENDPOINT: ' + evalue.id
                                     +         '<input name="endpoint_id" type="hidden" value="' + evalue.id + '"><br>'
                                     +         'TYPE: ' + evalue.type
                                     +         '<input name="endpoint_type" type="hidden" value="' + evalue.type + '"><br>'
                                     +         'VALUE:'
                                     +         '<input name="value" type="text" id="' + ep_tag + '_value" '
                                     +             'value="' + evalue.value + '"'
                                     +         '>'
                                     +         '<input type="submit" value="Save" id="' + ep_tag + '_button"><br>'
                                     +         '<input name="identity_id" type="hidden" value="' + ivalue.id + '">'
                                     +     '</form>'
                                     + '</div>'

                        id_entry.append(ep_entry)
                        $('#' + ep_tag + '_form').ajaxform({
//                            done: FIX ME LATER TO DISPLAY STATUS
                        });
                    });
                });
            });
        }
    });




})(jQuery);
