# Generated by Django 4.0.5 on 2023-01-23 05:13

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RareFndApp', '0049_contribution_contribution_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=ckeditor.fields.RichTextField(max_length=100000, null=True),
        ),
    ]
