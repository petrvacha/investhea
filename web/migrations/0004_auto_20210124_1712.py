# Generated by Django 3.1.4 on 2021-01-24 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20210104_2044'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('alternative_name', models.CharField(max_length=50, null=True)),
                ('country', models.PositiveSmallIntegerField(choices=[(1, 'USA'), (2, 'CZ')], default=1)),
            ],
        ),
        migrations.AddField(
            model_name='security',
            name='delisting_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='security',
            name='ipo_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='security',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='security',
            name='exchange',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='web.exchange'),
        ),
    ]
