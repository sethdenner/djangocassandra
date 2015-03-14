# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import knotis.contrib.quick.fields
import django_extensions.db.fields
import knotis.contrib.quick.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
        ('auth', '0002_auto_20150312_1932'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('password_reset_key', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=36, null=True, db_index=True, blank=True)),
                ('expires', knotis.contrib.quick.fields.QuickDateTimeField(default=None, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(null=True, max_length=254, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('_denormalized_knotis_auth_KnotisUser_username_pk', django_extensions.db.fields.UUIDField(auto=False, db_index=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('default_identity', knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='identity.Identity', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='UserXapiClientMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', knotis.contrib.quick.fields.QuickBooleanField(default=False, db_index=True)),
                ('pub_date', knotis.contrib.quick.fields.QuickDateTimeField(default=None, auto_now_add=True, null=True, verbose_name=b'date published')),
                ('client', knotis.contrib.quick.fields.QuickCharField(default=None, max_length=64, null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(knotis.contrib.quick.models.QuickModelBase, models.Model),
        ),
        migrations.CreateModel(
            name='KnotisUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='passwordreset',
            name='user',
            field=knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='knotis_auth.KnotisUser', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userinformation',
            name='user',
            field=knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='knotis_auth.KnotisUser', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userxapiclientmap',
            name='user',
            field=knotis.contrib.quick.fields.QuickForeignKey(default=None, blank=True, to='knotis_auth.KnotisUser', null=True),
            preserve_default=True,
        ),
    ]
