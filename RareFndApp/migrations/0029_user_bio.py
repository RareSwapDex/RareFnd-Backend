# Generated by Django 4.0.5 on 2022-10-21 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0028_alter_project_company_ubos'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.EmailField(blank=True, default='', max_length=10000, null=True),
        ),
    ]
