# Generated by Django 3.2.6 on 2021-12-01 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'verbose_name': 'Payments For Invoice'},
        ),
        migrations.AlterModelOptions(
            name='soldproduct',
            options={'verbose_name': 'Products In Invoice'},
        ),
    ]
