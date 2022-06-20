# Generated by Django 4.0.3 on 2022-04-14 18:16

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Номер телефона')),
                ('city', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=6, verbose_name='Активационный код')),
                ('tg_chat_id', models.CharField(blank=True, max_length=30, verbose_name='ID чата в телеграме ')),
                ('is_trader', models.BooleanField(default=False, verbose_name='Трейдер')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[('accepted', 'принято'), ('refused', 'отклонено'), ('on_consideration', 'на рассмотрении')], default=3)),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('birth_day', models.DateField()),
                ('passport_number', models.CharField(max_length=100, unique=True, verbose_name='Номер паспорта')),
                ('inn', models.CharField(max_length=14, unique=True, validators=[django.core.validators.RegexValidator(message='Неверный инн', regex='^(1|2){1}\\d{13}$')], verbose_name='Инн')),
                ('country', models.CharField(max_length=100, verbose_name='Страна проживания')),
                ('city', models.CharField(max_length=100, verbose_name='Город')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
            },
        ),
        migrations.CreateModel(
            name='Trader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verified', models.BooleanField(default=False, verbose_name='Верификация')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Трейдер',
                'verbose_name_plural': 'Трейдеры',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')], verbose_name='Оценка')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='users.trader', verbose_name='Оцененный трейдер')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь поставивший оценку')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='document/%y/%m/%d/', verbose_name='Фото')),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='users.document')),
            ],
            options={
                'verbose_name': 'Фото документа',
                'verbose_name_plural': 'Фото документов',
            },
        ),
        migrations.AddField(
            model_name='document',
            name='trader',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='document', to='users.trader'),
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Баланс пользователя')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='balance', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Баланс',
                'verbose_name_plural': 'Балансы',
            },
        ),
    ]