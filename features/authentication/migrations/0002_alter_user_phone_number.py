# Generated by Django 5.1.3 on 2024-11-20 06:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=11, null=True, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '09XXXXXXXXX'. Up to 11 digits allowed.", regex='^09\\d{9}$')], verbose_name='phone number'),
        ),
    ]