# Generated by Django 3.1.7 on 2021-04-29 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_social',
            field=models.BooleanField(default=0),
        ),
    ]
