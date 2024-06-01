import telebot
from dotenv import load_dotenv
import os
from src.retriever import Retriever

load_dotenv()
# Токен телеграм бота
TOKEN = os.getenv("TOKEN")

# Путь к архиву с данными
ZIP_PATH = os.getenv("ZIP_PATH")

# Инициализируем Retriever
retriever = Retriever(ZIP_PATH)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


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
