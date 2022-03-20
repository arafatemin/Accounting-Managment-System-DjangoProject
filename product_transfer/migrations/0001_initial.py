# Generated by Django 3.2.7 on 2021-09-30 01:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customuser', '0001_initial'),
        ('tax', '0001_initial'),
        ('organization', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('from_org', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transfer_from', to='organization.organization')),
                ('tax', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tax.tax')),
                ('to_org', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transfer_to', to='organization.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customuser.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='TransferedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.FloatField()),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('price', models.FloatField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_transfer.producttransfer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customuser.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='TransferReturnedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_transfer.transferedproduct')),
            ],
        ),
        migrations.CreateModel(
            name='TransferPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_transfer.producttransfer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_transferuser', to='customuser.customuser')),
            ],
        ),
    ]
