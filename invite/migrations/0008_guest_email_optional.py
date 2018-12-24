"""
Migration to make guests emails optional

Generated by Django 2.1.2 on 2018-12-24 14:31
"""
#pylint: disable=invalid-name

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    The migration to apply
    """
    dependencies = [
        ('invite', '0007_accompany_female'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='email',
            field=models.EmailField(max_length=254, blank=True, null=True,
                                    verbose_name='email address'),
        ),
    ]
