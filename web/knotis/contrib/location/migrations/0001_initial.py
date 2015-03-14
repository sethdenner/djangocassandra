# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('address', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=256, null=True, blank=True)),
                ('latitude', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('longitude', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='LocationItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('related_object_id', knotis.contrib.quick.fields.QuickUUIDField(default=None, editable=False, blank=True, null=True, db_index=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('location', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='location.Location', null=True)),
                ('related_content_type', knotis.contrib.quick.fields.QuickForeignKey(related_name='locationitem_related_set', default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
