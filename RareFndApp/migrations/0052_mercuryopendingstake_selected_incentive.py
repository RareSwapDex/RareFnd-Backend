# Generated by Django 4.0.5 on 2023-01-25 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0051_contribution_eligible_for_selected_incentive_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mercuryopendingstake',
            name='selected_incentive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='RareFndApp.incentive'),
        ),
    ]
