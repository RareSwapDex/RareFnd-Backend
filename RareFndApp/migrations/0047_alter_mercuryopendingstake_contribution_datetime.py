# Generated by Django 4.0.5 on 2023-01-06 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0046_mercuryopendingstake_contribution_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mercuryopendingstake',
            name='contribution_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
