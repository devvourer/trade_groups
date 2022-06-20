from django.db import models

from apps.users.models import User

from uuid import uuid4


class StatusChoices(models.TextChoices):
    SUCCESS = 'success', 'успешно'
    EXPECTATION = 'expectation', 'ожидание'
    NOT_SUCCESS = 'not_success', 'не успешно'


class PaymentOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                             related_name='payments', verbose_name='Пользователь')
    payment_order_id = models.UUIDField(default=uuid4, verbose_name='Идентификатор платежа (Yomoney)')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    # paid = models.BooleanField(default=False)
    status = models.CharField(choices=StatusChoices.choices,
                              default=StatusChoices.EXPECTATION, max_length=20, verbose_name='Статус')

    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'{self.user} : {self.amount}'


class Currency(models.Model):
    name = models.CharField(max_length=5, verbose_name='Имя валюты')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Курс по отношению к рублю')

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюта"

    def __str__(self):
        return f"{self.name} : {self.value}"


class PaymentOrderTether(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tether_payments', null=True)
    tx_id = models.CharField(max_length=260, blank=True, verbose_name='ID транзакции в binance')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма', null=True)
    status = models.CharField(choices=StatusChoices.choices,
                              default=StatusChoices.EXPECTATION, max_length=20, verbose_name='Статус')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Платеж tether'
        verbose_name_plural = 'Платежи tether'


class Withdraw(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='withdraws')
    address = models.CharField(max_length=250, verbose_name='адрес для вывода')
    amount = models.PositiveSmallIntegerField(verbose_name='Сумма')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(choices=StatusChoices.choices,
                              default=StatusChoices.EXPECTATION, max_length=20, verbose_name='Статус')

    class Meta:
        verbose_name = 'Вывод'
        verbose_name_plural = 'Выводы'
