# Generated by Django 3.2.6 on 2021-12-01 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fromstock', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productinstock',
            options={'verbose_name': 'Stock'},
        ),
        migrations.AlterModelOptions(
            name='productwithunit',
            options={'verbose_name': 'Products From Stock'},
        ),
    ]
