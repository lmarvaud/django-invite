"""
Migration to add event model

Generated by Django 2.1.4 on 2018-12-27 10:21
"""
#pylint: disable=invalid-name,line-too-long

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    The migration to apply
    """
    dependencies = [
        ('invite', '0008_guest_email_optional'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='name')),
                ('date', models.DateField(blank=True, null=True, verbose_name='date')),
                ('families', models.ManyToManyField(blank=True, related_name='invitations', to='invite.Family')),
            ],
            options={
                'verbose_name_plural': 'events',
                'verbose_name': 'event',
            },
        ),
    ]
