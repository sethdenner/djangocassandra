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
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('relation_type', knotis.contrib.quick.fields.QuickCharField(default=b'undefined', choices=[(b'undefined', b'Undefined'), (b'individual', b'Individual'), (b'superuser', b'Superuser'), (b'proprietor', b'Proprietor'), (b'manager', b'Manager'), (b'employee', b'Employee'), (b'establishment', b'Establishment'), (b'following', b'Following'), (b'likes', b'Likes'), (b'customer', b'Customer')], max_length=25, blank=True, null=True, db_index=True)),
                ('subject_object_id', knotis.contrib.quick.fields.QuickUUIDField(default=None, editable=False, blank=True, null=True, db_index=True)),
                ('related_object_id', knotis.contrib.quick.fields.QuickUUIDField(default=None, editable=False, blank=True, null=True, db_index=True)),
                ('description', knotis.contrib.quick.fields.QuickTextField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('related_content_type', knotis.contrib.quick.fields.QuickForeignKey(related_name='relation_related_set', default=None, blank=True, to='contenttypes.ContentType', null=True)),
                ('subject_content_type', knotis.contrib.quick.fields.QuickForeignKey(related_name='relation_subject_set', default=None, blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='RelationEmployee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('relation.relation',),
        ),
        migrations.CreateModel(
            name='RelationFollowing',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('relation.relation',),
        ),
        migrations.CreateModel(
            name='RelationProprietor',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('relation.relation',),
        ),
    ]
