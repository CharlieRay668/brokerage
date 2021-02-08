# Generated by Django 3.1.4 on 2021-02-03 01:58

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
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_type', models.IntegerField(choices=[(1, 'Limit'), (2, 'Market'), (3, 'Stop Market'), (4, 'Stop Limit'), (5, 'Trailing Stop %'), (6, 'Traling Stop $')])),
                ('order_expiration', models.IntegerField(choices=[(1, 'Day'), (2, 'GTC')])),
                ('order_quantity', models.IntegerField()),
                ('order_fill_price', models.IntegerField()),
                ('order_fill_happen', models.BooleanField()),
                ('order_execution_datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_id', models.TextField(default=None)),
                ('symbol', models.CharField(max_length=30)),
                ('quantity', models.IntegerField(default=None)),
                ('fill_price', models.FloatField(default=-999, editable=False)),
                ('position_info', models.JSONField(default=None)),
                ('order_action', models.IntegerField(choices=[(1, 'Buy'), (2, 'Sell'), (3, 'Buy to Cover'), (4, 'Sell Short')], default=1, editable=False)),
                ('order_type', models.IntegerField(choices=[(1, 'Limit'), (2, 'Market'), (3, 'Stop Market'), (4, 'Stop Limit'), (5, 'Trailing Stop %'), (6, 'Traling Stop $')], default=2)),
                ('order_expiration', models.IntegerField(choices=[(1, 'Day'), (2, 'GTC')], default='1')),
                ('order_execution_date', models.DateTimeField(default=None)),
                ('limit_price', models.IntegerField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
