"""
Generated by Django 2.1.2 on 2018-11-01 10:13
"""
# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    """Set a default value to the guest phone number"""
    dependencies = [
        ('invite', '0002_invite_female'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
