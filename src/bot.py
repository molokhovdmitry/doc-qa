import telebot
from dotenv import load_dotenv
import os
from src.retriever import Retriever
from src.data_loader import DataLoader


load_dotenv()
# Токен телеграм бота
TOKEN = os.getenv("TOKEN")

# Пути к файлам
ZIP_PATH = os.getenv("ZIP_PATH")
EXTRACT_DIR = os.getenv("EXTRACT_DIR")

# Загружаем данные
data = DataLoader(ZIP_PATH, EXTRACT_DIR)

# Инициализируем Retriever
retriever = Retriever(dataset=data)


# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


# Функция для печати документов
def pretty_print_docs(docs) -> str:
    text = "\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
    return text

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
        docs = retriever.answer(question=message.text)
        text = pretty_print_docs(docs)
        bot.send_message(message.from_user.id, text)


# Запускаем бота
bot.polling(none_stop=True, interval=0)
