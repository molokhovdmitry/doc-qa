import telebot
from dotenv import load_dotenv
import os
from retriever import Retriever
from data_loader import DataLoader


load_dotenv()


data = DataLoader(zip_path='D:\GitHub\doc-qa\data\data.zip',
                  extract_dir='D:\GitHub\doc-qa\data\extracted')

Retriever = Retriever(dataset=data)

# Токен телеграм бота
TOKEN = os.getenv("TOKEN")

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)
 
# Текстовый обработчик

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id,
                         "Привет, я телеграм-бот ПЭК,чем могу помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         "Напиши любой запрос к базе данных документов ПЭК.")
    else:                   # добавить функцию обработки запроса к langchain
        docs = Retriever.answer(question=message.text)
        for doc in docs:
            bot.send_message(message.from_user.id, doc.page_content)
            bot.send_message(message.from_user.id, doc.metadata['url'])
            bot.send_message(message.from_user.id, doc.metadata['department'])


# Запускаем бота
bot.polling(none_stop=True, interval=0)
