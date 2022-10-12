# Generated by Django 4.0.5 on 2022-10-11 17:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0025_alter_project_company_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='subscribed_users',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='Projects', to=settings.AUTH_USER_MODEL),
        ),
    ]
