# Generated by Django 3.2.6 on 2021-12-01 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_auto_20211201_2007'),
        ('customuser', '0002_customuser_organization'),
        ('purchase', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boughtproduct',
            options={'verbose_name': 'Products In Purchase'},
        ),
        migrations.AlterModelOptions(
            name='debt',
            options={'verbose_name': 'Vendor Debt'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'verbose_name': 'Vendor Payment'},
        ),
        migrations.CreateModel(
            name='DebtPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField()),
                ('note', models.TextField(blank=True, null=True)),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bank.bank')),
                ('debt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchase.debt')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debt_payment_user', to='customuser.customuser')),
            ],
            options={
                'verbose_name': 'Vendor Debt Payment',
            },
        ),
    ]
