from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.utils import timezone

from .models import TradeGroup, Trader
from apps.payments.models import PaymentOrderTether, Withdraw
from binance import Client
from decimal import Decimal
from apps.payments.utils import percent
from apps.telegram_bot.tasks import notify_admin

import logging

withdraw_logger = logging.getLogger('withdraw')
payment_logger = logging.getLogger('payment_tether')
withdraw_groups = logging.getLogger('withdraw_from_groups')


class BinanceAPI:

    def __init__(self):
        self.client = Client(settings.BINANCE_API, settings.BINANCE_SECRET)

    def withdraw_from_group(self, group: TradeGroup) -> Response:
        """Вывод средств с группы"""
        trader = group.trader
        trader_client = Client(trader.binance_api_key, trader.binance_secret_key)
        trader_deposit_address = trader_client.get_deposit_address(coin='USDT')['address']

        group.trader_binance_balance = Decimal(trader_client.get_asset_balance(asset='USDT')['free'])
        group.save(update_fields=['trader_binance_balance'])
        try:
            self.client.withdraw(coin='USDT', address=trader_deposit_address,
                                 amount=group.need_sum, name='Withdraw from sky invest')
            return Response({'message': 'Средства выведены на ваш кошелек'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            withdraw_groups.warning(f'{timezone.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                                    f' : withdraw_from_group error : {e}')
            return Response({'message': 'Ошибка вывода средств'}, status=status.HTTP_409_CONFLICT)

    def check_tx_id(self, order: PaymentOrderTether) -> Response:
        """Проверка txid"""
        tx_id = order.tx_id
        if PaymentOrderTether.objects.filter(tx_id=tx_id).exists():
            return Response({'message': 'tx_id_error'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            for item in self.client.get_deposit_history(coin='USDT'):
                if item['txId'] == tx_id or item['txId'].split()[2] == tx_id and item['status'] == 1:
                    order.status = 'success'
                    order.save(update_fields=['status'])

                    user_pocket = order.user.balance
                    user_pocket.balance += Decimal(item['amount'])
                    user_pocket.save(update_fields=['balance'])

                    notify_admin.delay({'payment': f"{order.user.phone_number} : "
                                                   f"{order.amount} USDT : "
                                                   f"{order.created}"})
                    return Response({'message': 'Успешно'}, status=status.HTTP_202_ACCEPTED)
            return Response({'message': 'Данный tx id не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            order.status = 'not_success'
            order.save(update_fields=['status'])
            payment_logger.warning(f'{timezone.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} : payment_error : {e}')
            return Response({'message': 'Системная ошибка'}, status=status.HTTP_409_CONFLICT)

    def get_deposit_address(self):
        return self.client.get_deposit_address(coin='USDT', network='TRX')['address']

    def withdraw(self, obj: Withdraw) -> Response:
        """Вывод средств"""
        try:
            self.client.withdraw(coin='USDT', address=obj.address, amount=obj.amount, name='Withdraw')
        except Exception as e:
            obj.status = 'not_success'
            obj.save(update_fields=['status'])
            withdraw_logger.warning(f'{timezone.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} : withdraw_error : {e}')
            return Response({'message': 'Системная ошибка'}, status=status.HTTP_409_CONFLICT)

        user_balance = obj.user.balance
        user_balance.balance -= obj.amount
        user_balance.save(update_fields=['balance'])
        obj.status = 'success'
        obj.save(update_fields=['status'])
        return Response({'message': 'Средства выведены на ваш кошелек'}, status=status.HTTP_202_ACCEPTED)

    def end_group(self, group: TradeGroup):
        """Окончание группы,  """
        try:
            trader = group.trader
            trader_client = Client(trader.binance_api_key, trader.binance_secret_key)

            trader_balance = Decimal(trader_client.get_asset_balance(asset='USDT')['free'])

            # общее количество usdt на момент окончания группы у трейдера
            remains = trader_balance - group.trader_binance_balance

            income = remains - Decimal(group.need_sum)  # Прибыль
            if income > 0:
                # Списание средств с баланса трейдера в пользу системы
                trader_client.withdraw(coin='USDT', address=self.client.get_deposit_address(coin='USDT'),
                                       amount=remains)
                trader_cash = income / 100 * group.percent_from_income  # Сколько получит трейдер
                # Вознаграждение трейдера
                self.client.withdraw(coin='USDT', address=trader_client.get_deposit_address(coin='USDT'),
                                     amount=Decimal(trader_cash))
                # прибыль поделится на всех инвесторов, в соотношении - сколько процентов от need_sum они инвестировали
                income = income - trader_cash  # общая прибыль с вычетом процента который получил трейдер
                for investor in group.investors.all():
                    # сколько он инвестировал от need_sum в процентах
                    invested_sum_percent = percent(investor.invested_sum, group.need_sum)
                    # сколько средств от прибыли получит инвестор
                    income_for_investor = (income / 100 * invested_sum_percent) + investor.invested_sum

                    investor_balance = investor.investor.balance
                    investor_balance.balance += income_for_investor
                    investor_balance.save(update_fields=['balance'])

                    investor.income = income
                    investor.save(update_fields=['income'])

        except Exception as e:
            pass

    def get_trade_history(self, trader: Trader):
        client = Client(trader.binance_api_key, trader.binance_secret_key)
        history = client.get_my_trades()

    @staticmethod
    def group_did_not_get_enough(group: TradeGroup):
        for membership in group.investors.all():
            investor_balance = membership.investor.balance
            investor_balance.balance += membership.invested_sum
            investor_balance.save(updated_fields=['balance'])
