# Generated by Django 4.0.5 on 2023-01-25 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0053_pendingcontribution_contribution_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='mercuryopendingstake',
            name='contributor_email',
            field=models.CharField(blank=True, default='None', max_length=254, null=True),
        ),
    ]
