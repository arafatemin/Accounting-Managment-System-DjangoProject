# Generated by Django 3.2.6 on 2021-12-10 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0005_auto_20211210_1858'),
        ('product_transfer', '0003_transferpayment_bank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orgdebtpayment',
            name='bank',
        ),
        migrations.RemoveField(
            model_name='transferpayment',
            name='bank',
        ),
        migrations.AddField(
            model_name='orgdebtpayment',
            name='from_bank',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='org_from_bank', to='bank.bank'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orgdebtpayment',
            name='to_bank',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='org_to_bank', to='bank.bank'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transferpayment',
            name='from_bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='out_payment', to='bank.bank'),
        ),
        migrations.AddField(
            model_name='transferpayment',
            name='to_bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='in_payment', to='bank.bank'),
        ),
    ]