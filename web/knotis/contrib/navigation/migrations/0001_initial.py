# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.fields
import knotis.contrib.quick.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NavigationItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('item_type', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=16, null=True, blank=True, choices=[(b'link', b'Link'), (b'header', b'Header'), (b'divider', b'Divider')])),
                ('title', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=32, null=True, blank=True)),
                ('uri', knotis.contrib.quick.fields.QuickURLField(default=None, null=True, blank=True)),
                ('menu_name', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=32, null=True, db_index=True, blank=True)),
                ('order', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('parent', knotis.contrib.quick.fields.QuickForeignKey(related_name='children', default=None, blank=True, to='navigation.NavigationItem', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
