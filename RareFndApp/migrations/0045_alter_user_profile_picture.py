# Generated by Django 4.0.5 on 2022-12-20 23:56

import RareFndApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0044_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=RareFndApp.models.get_users_files_directory),
        ),
    ]
