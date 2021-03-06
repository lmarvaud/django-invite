"""
Generated by Django 2.1.2 on 2018-10-31 15:22
"""
# pylint: disable=invalid-name
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Create family invite and accompany tables"""
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('number', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('invited_midday', models.BooleanField(default=False)),
                ('invited_afternoon', models.BooleanField(default=False)),
                ('invited_evening', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Family',
                'verbose_name_plural': 'Families',
            },
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='invites', to='invite.Family')),
            ],
        ),
        migrations.AddField(
            model_name='accompany',
            name='family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='accompanies', to='invite.Family'),
        ),
    ]
