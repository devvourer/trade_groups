# Generated by Django 4.0.3 on 2022-05-02 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copytrade', '0002_tradegroup_group_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradegroup',
            name='end_date',
            field=models.DateTimeField(default='2022-5-2', verbose_name='Дата окончания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tradegroup',
            name='start_date',
            field=models.DateTimeField(default='2022-5-2', verbose_name='Дата начала'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tradegroup',
            name='status',
            field=models.CharField(choices=[('started', 'стартовала'), ('recruited', 'набирается'), ('completed', 'завершена')], default='completed', max_length=20, verbose_name='Статус группы'),
            preserve_default=False,
        ),
    ]
