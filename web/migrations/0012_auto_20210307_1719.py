# Generated by Django 3.1.4 on 2021-03-07 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0011_auto_20210307_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userssecurities',
            name='direction',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BUY'), (2, 'SELL')]),
        ),
    ]