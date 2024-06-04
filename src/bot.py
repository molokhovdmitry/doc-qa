import telebot
from dotenv import load_dotenv
import os
from src.retriever import Retriever
import re

load_dotenv()
# Токен телеграм бота
TOKEN = os.getenv("TOKEN")

# Путь к архиву с данными
ZIP_PATH = os.getenv("ZIP_PATH")

# Инициализируем Retriever
retriever = Retriever(ZIP_PATH)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

pattern = "^[A-Za-zА-Яа-я0-9_]+\.zip$"


# Функция для преобразования словаря в строку
def answer_to_message(answer: dict) -> str:
    text = answer['text']
    url = answer['url']
    department = answer['department']
    full_html_name = answer['full_html_name']
    message = f"{text}\n\nОтдел: {department}\n{full_html_name}\n{url}"
    return message


# Текстовый обработчик
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id,
                         "Привет, я телеграм-бот ПЭК,чем могу помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         "Напиши любой запрос к базе данных документов ПЭК.")
        bot.send_message(message.from_user.id,
                         "Напиши /add_doc для обновления базы данных документов")
    elif message.text == "/add_doc":
        bot.send_message(message.from_user.id,
                         "Напиши имя файла в формате filename.zip")
        if re.match(pattern, message.text):
            retriever.add_doc(f"data/{message.text}")
            bot.send_message(message.from_user.id, "База данных обновлена")
        else:
            bot.send_message(message.from_user.id, "Неверное имя файла")
    else:
        answer_dict = retriever.answer(question=message.text)
        if answer_dict is None:
            bot.send_message(
                message.from_user.id,
                "Не получилось найти ответ."
            )
        else:
            answer_message = answer_to_message(answer_dict)
            bot.send_message(
                message.from_user.id,
                answer_message
            )


# Запускаем бота
print("Bot is ready...")
bot.polling(none_stop=True, interval=0)
