# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-25 10:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_post_is_featured'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='status',
            new_name='active',
        ),
    ]