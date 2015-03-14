# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('inventory', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('media', '0001_initial'),
        ('endpoint', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('offer_type', knotis.contrib.quick.fields.QuickIntegerField(default=0, null=True, db_index=True, blank=True, choices=[(0, b'Normal'), (1, b'Premium'), (2, b'Dark'), (3, b'Digital Offer Collection'), (4, b'Random Offer Collection'), (5, b'One Random Offer Collection')])),
                ('title', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=140, null=True, blank=True)),
                ('description', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, blank=True)),
                ('restrictions', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, blank=True)),
                ('start_time', knotis.contrib.quick.fields.QuickDateTimeField(default=None, null=True, blank=True)),
                ('end_time', knotis.contrib.quick.fields.QuickDateTimeField(default=None, null=True, blank=True)),
                ('stock', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, blank=True)),
                ('unlimited', knotis.contrib.quick.fields.QuickBooleanField(default=False)),
                ('purchased', knotis.contrib.quick.fields.QuickIntegerField(default=0, null=True, blank=True)),
                ('redeemed', knotis.contrib.quick.fields.QuickIntegerField(default=0, null=True, blank=True)),
                ('published', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('active', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('completed', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('last_purchase', knotis.contrib.quick.fields.QuickDateTimeField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('default_image', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='media.ImageInstance', null=True)),
                ('owner', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='OfferAvailability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('title', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=140, null=True, blank=True)),
                ('stock', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, blank=True)),
                ('purchased', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, blank=True)),
                ('price', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('available', knotis.contrib.quick.fields.QuickBooleanField(default=True, db_index=True)),
                ('end_time', knotis.contrib.quick.fields.QuickDateTimeField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('default_image', knotis.contrib.quick.fields.QuickForeignKey(related_name='offeravailability_offer_images', default=None, blank=True, to='media.ImageInstance', null=True)),
                ('identity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
                ('offer', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='offer.Offer', null=True)),
                ('profile_badge', knotis.contrib.quick.fields.QuickForeignKey(related_name='offeravailability_badge_images', default=None, blank=True, to='media.ImageInstance', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='OfferCollection',
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
            name='OfferCollectionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('page', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('offer', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='offer.Offer', null=True)),
                ('offer_collection', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='offer.OfferCollection', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='OfferItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('price_discount', knotis.contrib.quick.fields.QuickFloatField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('inventory', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='inventory.Inventory', null=True)),
                ('offer', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='offer.Offer', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='DigitalOfferCollection',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('offer.offer',),
        ),
        migrations.CreateModel(
            name='OfferPublish',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('endpoint.publish',),
        ),
    ]
