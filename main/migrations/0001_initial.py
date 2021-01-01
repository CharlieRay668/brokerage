# Generated by Django 3.1.4 on 2020-12-23 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EquityPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=30)),
                ('quantity', models.IntegerField()),
                ('action', models.IntegerField(choices=[(1, 'Buy'), (2, 'Sell'), (3, 'Buy to Cover'), (4, 'Sell Short')])),
                ('order_type', models.IntegerField(choices=[(1, 'Limit'), (2, 'Market'), (3, 'Stop Market'), (4, 'Stop Limit'), (5, 'Trailing Stop %'), (6, 'Traling Stop $')])),
                ('order_expiration', models.IntegerField(choices=[(1, 'Day'), (2, 'GTC')])),
                ('order_execution_date', models.DateTimeField()),
                ('fill_price', models.IntegerField(null=True)),
                ('limit_price', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OptionPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=30)),
                ('quantity', models.IntegerField()),
                ('action', models.IntegerField(choices=[(1, 'Buy'), (2, 'Sell'), (3, 'Buy to Cover'), (4, 'Sell Short')])),
                ('order_type', models.IntegerField(choices=[(1, 'Limit'), (2, 'Market'), (3, 'Stop Market'), (4, 'Stop Limit'), (5, 'Trailing Stop %'), (6, 'Traling Stop $')])),
                ('order_expiration', models.IntegerField(choices=[(1, 'Day'), (2, 'GTC')])),
                ('order_execution_date', models.DateTimeField()),
                ('fill_price', models.IntegerField(null=True)),
                ('limit_price', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
