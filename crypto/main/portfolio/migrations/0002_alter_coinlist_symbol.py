# Generated by Django 5.0 on 2024-10-22 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coinlist',
            name='symbol',
            field=models.CharField(max_length=100),
        ),
    ]
