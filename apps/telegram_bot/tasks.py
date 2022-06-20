from sky_invest_trading.celery import app
from apps.users.models import Trader, User
from apps.copytrade.models import Membership
from .tg_bot import bot


@app.task()
def notify_trader(membership_id: int) -> None:
    try:
        obj = Membership.objects.get(id=membership_id).select_related('group__trader__user', 'investor')
        bot.send_message(obj.group.trader.user.tg_chat_id, f'К вашей группе присоединился новый инвестор {obj.invesor.first_name}, '
                                                        f'инвестировав {obj.invested_sum}$')
    except:
        return None


@app.task()
def notify_admin(data: dict) -> None:
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        try:
            text = data['payment_yomoney']
            bot.send_message(admin.tg_chat_id, f"Пополнение через yomoney: {text}")

        except KeyError as e:
            text = data['payment']
            bot.send_message(admin.tg_chat_id, f"Пополнение: {text}")

