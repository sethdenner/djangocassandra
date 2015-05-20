<VirtualHost *:80>
ServerAdmin dev@example.com
ServerName dev.knotis.com

Alias /media/ /knotis.com/app/media/
Alias /static/ /knotis.com/app/static/
Alias /admin/media/ /knotis.com/venv/lib/python2.7/site-packages/django/contrib/admin/media/
Alias /admin/static/ /knotis.com/venv/lib/python2.7/site-packages/django/contrib/admin/static/
Alias /robots.txt /knotis.com/app/static/robots.txt
Alias /favicon.ico /knotis.com/app/static/favicon.ico

CustomLog "|/usr/sbin/rotatelogs /knotis.com/logs/access.log.%Y%m%d-%H%M%S 5M" combined
ErrorLog "|/usr/sbin/rotatelogs /knotis.com/logs/error.log.%Y%m%d-%H%M%S 5M"
LogLevel warn

WSGIDaemonProcess dev.knotis.com user=www-data group=www-data processes=1 threads=15 maximum-requests=10000 python-path=/knotis.com/venv/lib/python2.7/site-packages python-eggs=/knotis.com/run/eggs
WSGIProcessGroup dev.knotis.com
WSGIScriptAlias / /knotis.com/app/conf/apache/knotis.wsgi
WSGIPassAuthorization On

<Directory /knotis.com/app/static>
Order deny,allow
Allow from all
Options -Indexes FollowSymLinks
</Directory>

<Directory /knotis.com/app/conf/apache>
Order deny,allow
Allow from all
</Directory>

</VirtualHost>
