# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qrcode', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QrcodeIdMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(db_index=True)),
                ('new_qrcode', models.ForeignKey(to='qrcode.Qrcode')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
