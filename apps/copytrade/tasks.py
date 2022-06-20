from sky_invest_trading.celery import app

from .models import Membership, TradeGroup
from .services import BinanceAPI


@app.task()
def withdraw_after_join_to_group(membership_id: int) -> None:
    """Списание денег после присоединения инвестора к группе"""
    membership = Membership.objects.get(id=membership_id)
    balance = membership.investor.balance
    balance.balance -= membership.invested_sum
    balance.save()


@app.task()
def start_group(group_id: int) -> None:
    """Start group"""
    group: TradeGroup = TradeGroup.objects.get(id=group_id)
    amount = 0
    for i in group.memberships.all():
        amount += i.invested_sum
    if amount >= group.need_sum:
        group.status = TradeGroup.Status.STARTED
        group.save(update_fields=['status'])
    client = BinanceAPI()
    client.group_did_not_get_enough(group)
    group.delete()


@app.task()
def end_group(group_id: int) -> None:
    group: TradeGroup = TradeGroup.objects.get(id=group_id)
    client = BinanceAPI()
    client.end_group(group)
    group.status = TradeGroup.Status.COMPLETED
    group.save(update_fields=['status'])
