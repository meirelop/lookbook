# Generated by Django 2.2.6 on 2019-10-07 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icrawler', '0003_auto_20191007_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='look',
            name='img_url',
            field=models.URLField(max_length=2000, verbose_name='Location of look img'),
        ),
    ]
