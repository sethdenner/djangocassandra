# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.fields
import knotis.contrib.quick.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '__first__'),
        ('identity', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('stock', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('price', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('unlimited', knotis.contrib.quick.fields.QuickBooleanField(default=False)),
                ('perishable', knotis.contrib.quick.fields.QuickBooleanField(default=False)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('product', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='product.Product', null=True)),
                ('provider', knotis.contrib.quick.fields.QuickForeignKey(related_name='inventory_provider', default=None, blank=True, to='identity.Identity', null=True)),
                ('recipient', knotis.contrib.quick.fields.QuickForeignKey(related_name='inventory_recipient', default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
