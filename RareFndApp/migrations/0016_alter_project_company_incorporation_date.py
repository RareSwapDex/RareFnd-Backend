# Generated by Django 4.0.5 on 2022-09-27 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0015_remove_project_projectdata_alter_incentive_reserved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='company_incorporation_date',
            field=models.DateTimeField(default=None),
        ),
    ]
