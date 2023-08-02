# Generated by Django 4.1 on 2023-08-02 00:58

import RareFndApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("RareFndApp", "0069_rsvpsubscriber_alter_project_company_country_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="incentive",
            name="display_order",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="rsvp",
            name="thumbnail",
            field=models.ImageField(
                default="help.jpg",
                null=True,
                upload_to=RareFndApp.models.get_rsvp_files_directory,
            ),
        ),
    ]
