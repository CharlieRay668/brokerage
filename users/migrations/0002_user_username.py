# Generated by Django 3.1.4 on 2021-02-22 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.TextField(default='unkown', verbose_name='username'),
        ),
    ]
