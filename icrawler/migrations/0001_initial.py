# Generated by Django 2.2.6 on 2019-10-07 12:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Look',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_django', models.DateTimeField(auto_now_add=True)),
                ('modified_django', models.DateTimeField(auto_now=True)),
                ('img_url', models.URLField(verbose_name='Location of look img')),
                ('full_id', models.TextField(blank=True, verbose_name='Look full ID')),
                ('look_id', models.IntegerField(unique=True, verbose_name='Lookbook id')),
                ('hype', models.IntegerField(default=0, verbose_name='Hype rating')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Creation date')),
                ('country', models.TextField(verbose_name='Country')),
                ('hashtags', models.TextField(verbose_name='Hashtags contained')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScrapyItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=100, null=True)),
                ('data', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]