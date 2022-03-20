# Generated by Django 3.2.6 on 2021-12-02 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_auto_20211201_2007'),
        ('product_transfer', '0002_auto_20211201_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferpayment',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bank.bank'),
        ),
    ]
