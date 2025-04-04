# Generated by Django 4.0.5 on 2023-01-11 14:37

import RareFndApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0047_alter_mercuryopendingstake_contribution_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='wallet_address',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=RareFndApp.models.LowerCaseCharField(max_length=254, unique=True),
        ),
    ]
