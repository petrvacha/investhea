# Generated by Django 3.1.4 on 2021-01-25 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20210125_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]