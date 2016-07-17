# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-17 22:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseQuerie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('querie', models.CharField(max_length=1500)),
                ('database_connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database_manager.DatabaseConnection')),
            ],
        ),
    ]
