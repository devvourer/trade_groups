from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractUser

from .managers import UserManager, TraderQuerySet
from .utils import cript_symbols, get_roe

from binance import Client
from statistics import mean

from datetime import datetime


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Почта')
    phone_number = models.CharField(max_length=50, unique=True, verbose_name='Номер телефона', null=True, blank=True)

    code = models.CharField(max_length=6, verbose_name='Активационный код', blank=True)
    tg_chat_id = models.CharField(max_length=30, blank=True, verbose_name='ID чата в телеграмме ')

    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_trader = models.BooleanField(default=False, verbose_name='Трейдер')
    verified = models.BooleanField(default=False, verbose_name='Верификация')

    objects = UserManager()

    otp_for_login = models.BooleanField(default=False, verbose_name='2fa аутентификация для входа')
    otp_for_withdraw = models.BooleanField(default=False, verbose_name='2fa аутентификация для вывода')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name', 'is_trader']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email}'

    def otp_off(self):
        self.otp_for_withdraw = False
        self.otp_for_login = False
        self.save()

    def otp_on(self):
        self.otp_for_withdraw = True
        self.otp_for_login = True
        self.save()


class Trader(models.Model):
    """Модель Трейдера"""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='trader',
                                verbose_name='Пользователь', null=True)
    binance_api_key = models.CharField(max_length=100, blank=True, verbose_name='API ключ от аккаунта в binance')
    binance_secret_key = models.CharField(max_length=100, blank=True, verbose_name='SECRET ключ от аккаунта binance')

    objects = TraderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Трейдер'
        verbose_name_plural = 'Трейдеры'

    def __str__(self):
        return f"{self.user}"

    def get_rating(self):
        ratings = self.ratings.values_list('star', flat=True)
        if ratings.exists():
            lst_avg = mean(ratings)
            return round(lst_avg, 1)
        return 0

    def get_history_trades(self) -> 'list[dict]':

        client = Client(self.binance_api_key, self.binance_secret_key)
        data = []
        for symbol in cript_symbols:
            history = client.futures_account_trades(symbol=symbol)
            for trade in history:
                side = 'SHORT' if trade['side'] == 'SELL' else 'LONG'
                need_data = {'ticker': trade['symbol'],
                             'time': datetime.fromtimestamp(float(trade['time']) / 1000.0),
                             'side': side,
                             'price': trade['price'],
                             'qty': trade['qty'],
                             'realized_profit': trade['realizedPnl'],
                             'commission': trade['commission'],
                             }
                data.append(need_data)
        return data

    def get_open_trades(self) -> 'list[dict]':
        client = Client(self.binance_api_key, self.binance_secret_key)
        data = []
        for symbol in cript_symbols:

            open_orders = client.futures_position_information(symbol=symbol)
            for order in open_orders:
                size = float(order['positionAmt']) * float(order['leverage'])
                roe = get_roe(order['isolatedMargin'], order['unRealizedProfit'])
                need_data = {'symbol': order['symbol'],
                             'leverage': order['leverage'],  # кредитное плечо
                             'size': size,
                             'entry_price': order['entryPrice'],  # цена входа
                             'mark_price': order['markPrice'],
                             'liquidation_price': order['liquidationPrice'],
                             'margin': order['positionAmt'],
                             'pnl': {'pnl': order['unRealizedProfit'], 'roe': roe},  # PNL ROE
                             }
                data.append(need_data)
        return data


class Document(models.Model):
    """Документ для верификации трейдера"""

    class Status(models.TextChoices):
        ACCEPTED = 'accepted', 'принято'
        REFUSED = 'refused', 'отклонено'
        ON_CONSIDERATION = 'on_consideration', 'на рассмотрении'

    status = models.CharField(max_length=25, choices=Status.choices, default=Status.ON_CONSIDERATION)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='documents', null=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    birth_day = models.DateField(verbose_name='Дата рождения')
    passport_number = models.CharField(max_length=100, unique=True, verbose_name='Номер паспорта')
    inn = models.CharField(max_length=14, unique=True,
                           verbose_name='Инн')
    country = models.CharField(max_length=100, verbose_name='Страна проживания')
    city = models.CharField(max_length=100, verbose_name='Город')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return f"{self.user}"


class DocumentImage(models.Model):

    document = models.ForeignKey(Document, on_delete=models.SET_NULL, related_name='images', null=True)
    image = models.ImageField(upload_to=f'document/%y/%m/%d/', verbose_name='Фото', blank=True)

    class Meta:
        verbose_name = 'Фото документа'
        verbose_name_plural = 'Фото документов'


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='balance')
    balance = models.DecimalField(default=0, max_digits=7, decimal_places=2,
                                  verbose_name='Баланс пользователя')

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'

    def __str__(self):
        return f'{self.user} - {self.balance}'


class Rating(models.Model):

    class RatingStarChoices(models.IntegerChoices):
        ONE = 1, '1'
        TWO = 2, '2'
        THREE = 3, '3'
        FOUR = 4, '4'
        FIVE = 5, '5'
        SIX = 6, '6'
        SEVEN = 7, '7'
        EIGHT = 8, '8'
        NINE = 9, '9'
        TEN = 10, '10'

    star = models.PositiveSmallIntegerField(choices=RatingStarChoices.choices, verbose_name='Оценка')
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE,
                               related_name='ratings', verbose_name='Оцененный трейдер')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, verbose_name='Пользователь поставивший оценку')

    def __str__(self):
        return f"{self.trader} {self.star}- оцененный трейдер"


class Banner(models.Model):
    """Баннер для сайта"""
    image = models.ImageField(upload_to='banner', verbose_name='Фото баннера')

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннер'


class QA(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        verbose_name = 'Q&A'
        verbose_name_plural = 'Q&A'

    def __str__(self):
        return f"{self.question}"
