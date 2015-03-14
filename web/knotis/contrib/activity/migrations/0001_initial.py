# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('knotis_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('ip_address', knotis.contrib.quick.fields.QuickIPAddressField(default=None, null=True, db_index=True, blank=True)),
                ('activity_type', knotis.contrib.quick.fields.QuickIntegerField(default=-1, null=True, db_index=True, blank=True, choices=[(0, b'Request'), (1, b'Login'), (2, b'Logout'), (3, b'Sign_up'), (4, b'Purchase'), (5, b'Redeem'), (6, b'Promo Code'), (7, b'Connect a Random Offer Collection')])),
                ('application', knotis.contrib.quick.fields.QuickCharField(default=None, choices=[(b'knotisweb', b'Knotis Web'), (b'knotismobile', b'Knotis Mobile')], max_length=64, blank=True, null=True, db_index=True)),
                ('context', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, blank=True)),
                ('url_path', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=1024, null=True, blank=True)),
                ('authenticated_user', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='knotis_auth.KnotisUser', null=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('identity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='ActivityRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('related_object_id', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=32, null=True, blank=True)),
                ('activity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='activity.Activity', null=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('related_content_type', knotis.contrib.quick.fields.QuickForeignKey(related_name='activity_activityrelation_related_content_types', default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
    ]
