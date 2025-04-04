# Generated by Django 4.0.5 on 2022-10-03 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0020_country_iso_country_iso3_country_nicename_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='iso',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='iso3',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='nicename',
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='numcode',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='phonecode',
            field=models.IntegerField(null=True),
        ),
    ]
