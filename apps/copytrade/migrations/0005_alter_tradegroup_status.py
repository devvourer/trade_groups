# Generated by Django 4.0.3 on 2022-05-26 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copytrade', '0004_alter_membership_investor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradegroup',
            name='status',
            field=models.CharField(choices=[('started', 'стартовала'), ('recruited', 'набирается'), ('completed', 'завершена')], default='recruited', max_length=20, verbose_name='Статус группы'),
        ),
    ]
