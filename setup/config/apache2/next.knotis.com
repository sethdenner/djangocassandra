<VirtualHost *:80>
ServerAdmin seth.adam.denner@gmail.com
ServerName next.knotis.com

Alias /static/ /srv/knotis/app/static/
Alias /admin/static/ /srv/knotis/venv/lib/python2.7/site-packages/django/contrib/admin/static/
Alias /robots.txt /srv/knotis/app/static/robots.txt
Alias /favicon.ico /srv/knotis/app/static/favicon.ico

CustomLog "|/usr/sbin/rotatelogs /srv/knotis/logs/access.log.%Y%m%d-%H%M%S 5M" combined
ErrorLog "|/usr/sbin/rotatelogs /srv/knotis/logs/error.log.%Y%m%d-%H%M%S 5M"
LogLevel warn

WSGIDaemonProcess next.knotis.com user=knotis group=knotis processes=1 threads=15 maximum-requests=10000 python-path=/srv/knotis/venv/lib/python2.7/site-packages python-eggs=/srv/knotis/run/eggs
WSGIProcessGroup next.knotis.com
WSGIScriptAlias / /srv/knotis/app/conf/apache/knotis.wsgi
WSGIPassAuthorization On

<Directory /srv/knotis/app/static>
Order deny,allow
Allow from all
Options -Indexes FollowSymLinks
</Directory>

<Directory /srv/knotis/app/conf/apache>
Order deny,allow
Allow from all
</Directory>

</VirtualHost>