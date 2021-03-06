"""
Generated by Django 2.1.2 on 2018-11-02 17:12
"""
#pylint: disable=invalid-name
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Set verbose name to invite models"""
    dependencies = [
        ('invite', '0005_rename_guest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accompany',
            options={'verbose_name': 'accompany'},
        ),
        migrations.AlterModelOptions(
            name='family',
            options={'verbose_name': 'family', 'verbose_name_plural': 'families'},
        ),
        migrations.AlterModelOptions(
            name='guest',
            options={'verbose_name': 'Guest'},
        ),
        migrations.AlterField(
            model_name='accompany',
            name='family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='accompanies', to='invite.Family',
                                    verbose_name='family'),
        ),
        migrations.AlterField(
            model_name='accompany',
            name='name',
            field=models.CharField(max_length=64, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='accompany',
            name='number',
            field=models.IntegerField(default=1, verbose_name='number of person'),
        ),
        migrations.AlterField(
            model_name='family',
            name='host',
            field=models.CharField(max_length=32, verbose_name='principal host'),
        ),
        migrations.AlterField(
            model_name='family',
            name='invited_afternoon',
            field=models.BooleanField(default=False, verbose_name='is invite the afternoon'),
        ),
        migrations.AlterField(
            model_name='family',
            name='invited_evening',
            field=models.BooleanField(default=True, verbose_name='is invite at the party'),
        ),
        migrations.AlterField(
            model_name='family',
            name='invited_midday',
            field=models.BooleanField(default=False, verbose_name='is invite on lunch'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='guests', to='invite.Family',
                                    verbose_name='family'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='female',
            field=models.BooleanField(default=False, verbose_name='is a female'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='name',
            field=models.CharField(max_length=64, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20,
                                   verbose_name='phone number'),
        ),
    ]
