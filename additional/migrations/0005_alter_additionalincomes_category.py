# Generated by Django 3.2.6 on 2021-12-07 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('additional', '0004_additionalincomes_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalincomes',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='additional.incomecategory'),
        ),
    ]