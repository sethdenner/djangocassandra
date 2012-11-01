<VirtualHost *:80>
ServerAdmin seth@knotis.com
ServerName 74.121.189.146

Alias /media/ /srv/knotis/media/
Alias /static/ /srv/knotis/static/
Alias /admin/media/ /srv/knotis/venv/lib/python2.7/site-packages/django/contrib/admin/media/
Alias /robots.txt /srv/knotis/web/app/robots.txt
Alias /favicon.ico /srv/knotis/web/app/media/favicon.ico

CustomLog "|/usr/sbin/rotatelogs /srv/knotis/logs/access.log.%Y%m%d-%H%M%S 5M" combined
ErrorLog "|/usr/sbin/rotatelogs /srv/knotis/logs/error.log.%Y%m%d-%H%M%S 5M"
LogLevel warn

WSGIDaemonProcess int.knotis.com user=knotis-server group=knotis-server processes=1 threads=15 maximum-requests=10000 python-path=/srv/knotis/venv/lib/python2.7/site-packages python-eggs=/srv/knotis/run/eggs
WSGIProcessGroup int.knotis.com
WSGIScriptAlias / /srv/knotis/app/conf/apache/django.wsgi

<Directory /srv/knotis/media>
Order deny,allow
Allow from all
Options -Indexes FollowSymLinks
</Directory>

<Directory /srv/knotis/static>
Order deny,allow
Allow from all
Options -Indexes FollowSymLinks
</Directory>

<Directory /srv/knotis/app/conf/apache>
Order deny,allow
Allow from all
</Directory>

</VirtualHost>
