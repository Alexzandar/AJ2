# Generated by Django 2.1.3 on 2019-10-25 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('masters', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CadencySetting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cadency_system_url', models.TextField()),
                ('subscription_key', models.CharField(max_length=20)),
                ('host', models.CharField(max_length=250)),
                ('content_type', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('cust_id', models.ForeignKey(db_column='cust_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.Customer')),
            ],
            options={
                'db_table': 'bot_cadency_settings',
            },
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tcode', models.CharField(max_length=50)),
                ('program_name', models.CharField(max_length=50)),
                ('tcode_name', models.CharField(max_length=20)),
                ('variant_name', models.CharField(max_length=20)),
                ('variant_type', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('tcode_cat', models.ForeignKey(db_column='tcode_cat', default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.TcodeCategory')),
            ],
            options={
                'db_table': 'bot_library',
            },
        ),
        migrations.CreateModel(
            name='VariantDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('v_type', models.CharField(max_length=20)),
                ('v_option', models.CharField(max_length=20)),
                ('v_sign', models.CharField(max_length=20)),
                ('low', models.CharField(max_length=100)),
                ('high', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'bot_variant_details',
            },
        ),
        migrations.CreateModel(
            name='VariantMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tcode', models.CharField(max_length=50)),
                ('bot_id', models.CharField(max_length=50)),
                ('program_name', models.CharField(max_length=50)),
                ('variant_name', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('status', models.CharField(max_length=20)),
                ('output_type', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('cust_id', models.ForeignKey(db_column='cust_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.Customer')),
                ('cust_system_id', models.ForeignKey(db_column='cust_system_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.CustomerSystem')),
            ],
            options={
                'db_table': 'bot_variant_master',
            },
        ),
        migrations.AddField(
            model_name='variantdetail',
            name='v_master_id',
            field=models.ForeignKey(db_column='v_master_id', default=1, on_delete=django.db.models.deletion.CASCADE, to='settings.VariantMaster'),
        ),
    ]
