# Generated by Django 3.1.4 on 2021-01-25 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20210124_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
