# Generated by Django 4.0.5 on 2022-09-24 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0007_project_address_project_aproved_project_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='company_incorporation_date',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
