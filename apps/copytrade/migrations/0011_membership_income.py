# Generated by Django 4.0.3 on 2022-06-08 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copytrade', '0010_copytrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='income',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Прибыль'),
        ),
    ]
