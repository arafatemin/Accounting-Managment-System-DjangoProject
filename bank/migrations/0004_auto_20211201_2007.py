# Generated by Django 3.2.6 on 2021-12-01 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0003_bank_organization'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transfer',
            options={'verbose_name': 'Money Transfers'},
        ),
        migrations.AlterField(
            model_name='transfer',
            name='amount',
            field=models.FloatField(),
        ),
    ]
