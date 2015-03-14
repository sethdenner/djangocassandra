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
            name='Identity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('identity_type', knotis.contrib.quick.fields.QuickIntegerField(default=-1, null=True, blank=True, choices=[(0, b'Individual'), (1, b'Business'), (2, b'Establishment'), (3, b'Super User'), (-1, b'Undefined')])),
                ('name', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=80, null=True, verbose_name='Identity Name', blank=True)),
                ('backend_name', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=80, blank=True, null=True, verbose_name='Backend Name', db_index=True)),
                ('description', knotis.contrib.quick.fields.QuickTextField(default=None, null=True, verbose_name='Describe the Identity', blank=True)),
                ('available', knotis.contrib.quick.fields.QuickBooleanField(default=True, db_index=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='IdentityVariables',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('app', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=32, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('identity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='IdentityBusiness',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('identity.identity',),
        ),
        migrations.CreateModel(
            name='IdentityEstablishment',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('identity.identity',),
        ),
        migrations.CreateModel(
            name='IdentityIndividual',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('identity.identity',),
        ),
        migrations.CreateModel(
            name='IdentitySuperUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('identity.identity',),
        ),
    ]
