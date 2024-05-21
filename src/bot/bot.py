import telebot
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()


# Токен телеграм бота
TOKEN = os.getenv("TOKEN")

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Текстовый обработчик
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, я телеграм-бот ПЭК,чем могу помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши любой запрос к базе данных документов ПЭК.")
    else:                   # добавить функцию обработки запроса к langchain
        bot.send_message(message.from_user.id, message.text)


# Запускаем бота
bot.polling(none_stop=True, interval=0)
