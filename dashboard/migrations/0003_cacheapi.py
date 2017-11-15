# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-29 14:21
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20170615_1010'),
    ]

    operations = [
        migrations.CreateModel(
            name='CacheAPI',
            fields=[
                ('cache_api_id', models.AutoField(primary_key=True, serialize=False)),
                ('base_url', models.URLField(max_length=800)),
                ('resource', models.CharField(max_length=200)),
                ('request_args', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=400), default=list, size=None)),
                ('request_kwargs', models.CharField(max_length=1000)),
                ('response_content', models.TextField(max_length=10000)),
                ('response_content_json', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('expiry', models.DateTimeField()),
            ],
            options={
                'db_table': 'ts_cacheapi',
            },
        ),
    ]