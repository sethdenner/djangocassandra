# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Qrcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('uri', knotis.contrib.quick.fields.QuickURLField(default=None, null=True, blank=True)),
                ('qrcode_type', knotis.contrib.quick.fields.QuickCharField(default=b'profile', choices=[(b'profile', b'Business Profile'), (b'link', b'External Link'), (b'video', b'Video'), (b'offer', b'Offer')], max_length=16, blank=True, null=True, db_index=True)),
                ('hits', knotis.contrib.quick.fields.QuickIntegerField(default=0, null=True, blank=True)),
                ('last_hit', knotis.contrib.quick.fields.QuickDateTimeField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('owner', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('uri', knotis.contrib.quick.fields.QuickURLField(default=None, null=True, db_index=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('identity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
                ('qrcode', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='qrcode.Qrcode', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
