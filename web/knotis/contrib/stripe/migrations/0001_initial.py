# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.fields
import knotis.contrib.quick.models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('stripe_id', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=256, null=True, blank=True)),
                ('description', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('identity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
