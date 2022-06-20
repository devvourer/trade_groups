import uuid

from django.db import models
from django.core.validators import MaxValueValidator

from apps.users.models import Trader, User

from .querysets import GroupQuerySet


class TradeGroup(models.Model):
    """Модель группы трейдера"""

    class GroupType(models.TextChoices):
        TRADE = 'trade', 'трейдинг'
        OTHER = 'other', 'другое'
        ICO = 'ico', 'ico'

    class Status(models.TextChoices):
        STARTED = 'started', 'стартовала'
        RECRUITED = 'recruited', 'набирается'
        COMPLETED = 'completed', 'завершена'

    trader = models.ForeignKey(Trader, on_delete=models.SET_NULL,
                               null=True, related_name='groups', verbose_name='Создатель')
    group_type = models.CharField(max_length=10, choices=GroupType.choices, verbose_name='Тип группы')
    title = models.CharField(max_length=150, verbose_name='Название')
    slug = models.SlugField(max_length=150, unique=True, default=uuid.uuid4)
    description = models.CharField(max_length=500, verbose_name='Описание')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    investors = models.ManyToManyField(User, verbose_name='Инвесторы', through='Membership')
    group_size = models.PositiveSmallIntegerField(
        default=5,
        verbose_name='Максимальное количество инвесторов',
    )
    need_sum = models.PositiveSmallIntegerField(verbose_name='Необходимая сумма')
    min_entry_sum = models.PositiveSmallIntegerField(verbose_name='Минимальная сумма входа')
    max_entry_sum = models.PositiveSmallIntegerField(verbose_name='Максимальная сумма входа')

    percent_from_income = models.PositiveSmallIntegerField(verbose_name='Процент от прибыли',
                                                           validators=[MaxValueValidator(100)])
    trader_binance_balance = models.DecimalField(max_digits=10,
                                                 decimal_places=2,
                                                 verbose_name='Баланс трейдера в binance на момент вывода средств',
                                                 null=True)
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.RECRUITED, verbose_name='Статус группы')
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(verbose_name='Дата окончания')

    objects = GroupQuerySet.as_manager()

    class Meta:
        verbose_name = 'Группа трейдера'
        verbose_name_plural = 'Группы трейдеров'

    def __str__(self):
        return f"{self.trader} : {self.title} : {self.id}"


class Membership(models.Model):
    """Модель членства инвесторов в TradeGroup"""
    investor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='memberships')
    group = models.ForeignKey(TradeGroup, on_delete=models.SET_NULL, null=True, related_name='memberships')
    date_joined = models.DateTimeField(auto_now_add=True)
    invested_sum = models.PositiveSmallIntegerField(verbose_name="Инвестированная сумма")
    income = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name='Прибыль')

    class Meta:
        verbose_name = 'Членство в группе'
        verbose_name_plural = 'Членства в группах'

    def __str__(self):
        return f'{self.group} : {self.investor}'


class CopyTrade(models.Model):
    pass
