# Generated by Django 3.2.7 on 2021-09-30 01:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bank', '0001_initial'),
        ('additional', '0001_initial'),
        ('customuser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='outcomecategory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='out_cat_user', to='customuser.customuser'),
        ),
        migrations.AddField(
            model_name='additionaloutcomes',
            name='bank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bank.bank'),
        ),
        migrations.AddField(
            model_name='additionaloutcomes',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='additional.outcomecategory'),
        ),
        migrations.AddField(
            model_name='additionaloutcomes',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='a_o_user', to='customuser.customuser'),
        ),
        migrations.AddField(
            model_name='additionalincomes',
            name='bank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bank.bank'),
        ),
        migrations.AddField(
            model_name='additionalincomes',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_user', to='customuser.customuser'),
        ),
    ]
