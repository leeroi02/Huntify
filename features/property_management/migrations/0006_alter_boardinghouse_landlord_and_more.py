# Generated by Django 5.1.3 on 2024-11-25 04:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_management', '0005_alter_boardingroomtenant_boarding_room_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='boardinghouse',
            name='landlord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boarding_houses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='booking',
            name='boarding_room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='property_management.boardingroom'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
