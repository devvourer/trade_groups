from sky_invest_trading.celery import app
from django.conf import settings

from apps.telegram_bot.tasks import notify_admin
from .models import PaymentOrder
from .utils import convert_to_usd
from decimal import Decimal

import hashlib


@app.task()
def yomoney_payment_handler(request) -> None:
    data = request.POST
    str_list = [
        str(data['notification_type']),
        str(data['operation_id']),
        str(data['amount']),
        str(data['currency']),
        str(data['datetime']),
        str(data['sender']),
        str(data['codepro']),
        str(settings.YOMONEY_SECRET),
        str(data['label'])
    ]
    sha = ''
    for i in str_list:
        if i != '':
            sha += i + '&'
    hash_object = hashlib.sha1(bytes(sha[0:-1], 'utf-8')).hexdigest()

    if hash_object == data['sha1_hash']:
        payment_order = PaymentOrder.objects.select_related('user__balance').get(payment_order_id=data['label'])

        if str(data['notification_type']) == 'card-incoming':
            amount = float(data['amount'])
            if amount >= payment_order.amount:
                user_pocket = payment_order.user.balance

                payment_order.status = 'success'
                payment_order.save(update_fields=['status'])

                user_pocket.balance += Decimal(data['amount'])
                user_pocket.save(update_fields=['balance'])

                notify_admin.delay({'payment_yomoney': f'{payment_order.user.phone_number} : '
                                                       f'{payment_order.amount} USDT : '
                                                       f'{payment_order.created}'})

        if convert_to_usd(float(data['withdraw_amount'])) >= payment_order.amount:
            user_pocket = payment_order.user.balance

            payment_order.status = 'success'
            payment_order.save(update_fields=['status'])

            user_pocket.balance += Decimal(data['amount'])
            user_pocket.save(update_fields=['balance'])
