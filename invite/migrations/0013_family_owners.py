# Generated by Django 2.1.5 on 2019-04-15 06:30
# pylint: disable=invalid-name,missing-docstring
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invite', '0012_joineddocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='owners',
            field=models.ManyToManyField(editable=False, to=settings.AUTH_USER_MODEL),
        ),
    ]