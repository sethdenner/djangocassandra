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
            name='PromoCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('promo_code_type', knotis.contrib.quick.fields.QuickIntegerField(default=-1, null=True, blank=True, choices=[(0, b'Random Offer Collection'), (1, b'Offer Collection'), (-1, b'Undefined')])),
                ('value', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=64, null=True, blank=True)),
                ('context', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
