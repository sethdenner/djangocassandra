# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('image', sorl.thumbnail.fields.ImageField(height_field=b'height', width_field=b'width', upload_to=b'images/')),
                ('width', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('height', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('owner', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='ImageInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('related_object_id', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=36, null=True, db_index=True, blank=True)),
                ('context', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=50, null=True, db_index=True, blank=True)),
                ('primary', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('crop_left', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('crop_top', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('crop_width', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('crop_height', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('image', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='media.Image', null=True)),
                ('owner', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
