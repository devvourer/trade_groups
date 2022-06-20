# Generated by Django 4.0.3 on 2022-05-24 17:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('copytrade', '0003_tradegroup_end_date_tradegroup_start_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='investor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='memberships', to=settings.AUTH_USER_MODEL),
        ),
    ]
