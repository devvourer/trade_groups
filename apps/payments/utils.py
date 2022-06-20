from decimal import Decimal
from typing import Union

from .models import Currency


def convert_to_usd(amount: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
    currency = Currency.objects.get(name='usd')
    heft = amount / currency.value
    return round(heft * 1, 2)


def percent(part, whole) -> Decimal:
    percent = 100 * (Decimal(part) / Decimal(whole))
    return Decimal(percent)
