from django.conf import settings
from .models import Currency

import requests


class YooMoneyMixin:

    url = 'https://yoomoney.ru/quickpay/confirm.xml'

    @staticmethod
    def convert_to_rub(amount: int):
        usd = Currency.objects.get(name='usd')
        heft = amount * usd.value
        return round(heft * 1, 2)

    def get_payment_url_for_yomoney(self, amount: int, payment_id: str) -> str:
        params = {
            'receiver': settings.YOOMONEY_POCKET,
            'quickpay-form': 'small',
            'targets': 'Пополнение баланса Sky invest',
            'paymentType': 'PC',
            'sum': self.convert_to_rub(amount),
            'formcomment': 'Пополнение баланса Sky invest',
            'short-dest': 'Пополнение баланса Sky invest',
            'label': payment_id,
            'successURL': 'https://trusttrade.pro'
        }
        redirect_url = requests.Request(url=self.url, params=params).prepare().url
        return redirect_url
