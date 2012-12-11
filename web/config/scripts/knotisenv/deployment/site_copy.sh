#===============================#
#                               #
#    expects ${1} to be the     #
#    directory to copy          #
#                               #
#===============================#

# Backup old version of the site
if [[ -d /srv/knotis/app/web ]] ; then
    mkdir -p /srv/knotis/archive/ 2> /dev/null
    tar -czf /srv/knotis/archive/knotis_"$(date +%Y_%m_%d_%H%M%S)".tar.gz /srv/knotis/app/web
    rm -rf /srv/knotis/app/prev 2> /dev/null
    mv -f /srv/knotis/app/web /srv/knotis/app/prev

fi

cp ${1} /srv/knotis/app/web
