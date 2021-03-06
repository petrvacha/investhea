# Generated by Django 3.1.4 on 2021-07-11 09:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0023_auto_20210707_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='ordering',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='currency',
            name='symbol',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='usersmoneytransaction',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.currency'),
            preserve_default=False,
        ),
    ]
