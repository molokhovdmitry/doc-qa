import telebot
from telebot import types

# Токен телеграм бота
TOKEN = '6724916194:AAGTp_bZ_MN-kGkvQu9lOf71HCoF_hLElEY'

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, я телеграм-бот ПЭК, чем могу помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши любой запрос к базе данных документов")
    else:
        bot.send_message(message.from_user.id, message.text)


bot.polling(none_stop=True, interval=0)
