#===============================#
#                               #
#    expects ${1} to be the     #
#    directory to copy          #
#                               #
#===============================#

rm -rf /srv/knotis/app/prev 2> /dev/null
mv -f /srv/knotis/app/web /srv/knotis/app/prev
cp ${1} /srv/knotis/app/web
