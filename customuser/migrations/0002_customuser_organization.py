# Generated by Django 3.2.7 on 2021-09-30 01:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        ('customuser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_organization', to='organization.organization'),
        ),
    ]
