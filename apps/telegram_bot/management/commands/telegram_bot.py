from django.core.management.base import BaseCommand

from apps.telegram_bot.tg_bot import bot


class Command(BaseCommand):
    help = 'Start polling telegram bot'

    def handle(self, *args, **options):
        bot.infinity_polling()
