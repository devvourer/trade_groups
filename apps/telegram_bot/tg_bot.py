import telebot

from telebot import types
from decouple import config
from apps.users.models import User

token = config('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(token)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn1 = types.KeyboardButton('да')
btn2 = types.KeyboardButton('нет')
keyboard.add(btn1, btn2)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Вас приветствует бот sky invest!')
    bot.send_message(message.chat.id,
                     'Для получения уведомлений напишите ваш email привязанный к вашему аккаунту на sky invest')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    print(message.text)
    if message.text == 'да':
        bot.send_message(message.chat.id,
                         'Принято, теперь мы будем присылать уведомления сюда',
                         reply_markup=types.ReplyKeyboardRemove())

    elif message.text == 'нет':
        bot.send_message(message.chat.id, 'Введите email еще раз')

    else:
        try:
            user = User.objects.get(email=message.text)
            if not user.tg_chat_id:
                user.tg_chat_id = message.chat.id
                user.save()

            bot.send_message(message.chat.id,
                             f'{user.first_name} {user.last_name} {user.phone_number} - это ваш аккаунт?',
                             reply_markup=keyboard)

        except Exception as e:
            bot.send_message(message.chat.id,
                             f'Пользователь с таким email не найден, убедитесь что вы ввели правильный email')

