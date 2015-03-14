# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0001_initial'),
        ('identity', '0001_initial'),
        ('inventory', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('transaction_type', knotis.contrib.quick.fields.QuickCharField(default=None, choices=[(b'purchase', b'Purchase'), (b'redemption', b'Redemption'), (b'cancelation', b'Cancelation'), (b'return', b'Return'), (b'refund', b'Refund'), (b'transfer', b'Transfer'), (b'transaction_transfer', b'Transaction Transfer'), (b'dark_purchase', b'Dark Purchase')], max_length=64, blank=True, null=True, db_index=True)),
                ('transaction_context', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, db_index=True, blank=True)),
                ('reverted', knotis.contrib.quick.fields.QuickBooleanField(default=False)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('offer', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='offer.Offer', null=True)),
                ('owner', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='TransactionCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('neighborhood', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='TransactionCollectionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('page', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, db_index=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('transaction', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='transaction.Transaction', null=True)),
                ('transaction_collection', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='transaction.TransactionCollection', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('transaction_context', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, db_index=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('inventory', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='inventory.Inventory', null=True)),
                ('transaction', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='transaction.Transaction', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
