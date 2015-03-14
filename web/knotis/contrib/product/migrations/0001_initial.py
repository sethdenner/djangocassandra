# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.fields
import knotis.contrib.quick.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('product_type', knotis.contrib.quick.fields.QuickCharField(default=None, choices=[(b'physical', b'Physical'), (b'event', b'Event'), (b'service', b'Service'), (b'currency', b'Currency'), (b'digital', b'Digital'), (b'credit', b'Credit')], max_length=16, blank=True, null=True, db_index=True)),
                ('title', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=140, null=True, db_index=True, blank=True)),
                ('description', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=140, null=True, blank=True)),
                ('public', knotis.contrib.quick.fields.QuickBooleanField(default=True, db_index=True)),
                ('sku', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=32, null=True, db_index=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('primary_image', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='media.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
