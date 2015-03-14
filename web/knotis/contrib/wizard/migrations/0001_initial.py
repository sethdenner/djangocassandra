# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.models
import knotis.contrib.quick.fields


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WizardProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('wizard_name', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=16, null=True, db_index=True, blank=True)),
                ('query_string', knotis.contrib.quick.fields.QuickCharField(default=b'', max_length=1024, null=True, db_index=True, blank=True)),
                ('completed', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='WizardStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('action', knotis.contrib.quick.fields.QuickURLField(default=None, null=True, db_index=True, blank=True)),
                ('order', knotis.contrib.quick.fields.QuickIntegerField(default=None, null=True, blank=True)),
                ('wizard_name', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=16, null=True, db_index=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.AddField(
            model_name='wizardprogress',
            name='current_step',
            field=knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='wizard.WizardStep', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='wizardprogress',
            name='identity',
            field=knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True),
            preserve_default=True,
        ),
    ]
