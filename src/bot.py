from dotenv import load_dotenv
from retriever import Retriever
import telebot
import os
import re
import csv

USERS_FILE = 'data/users.csv'
ADMINS_FILE = 'data/admins.csv'


load_dotenv()
# Токен телеграм бота
TOKEN = os.getenv("TOKEN")

# Путь к архиву с данными
ZIP_PATH = os.getenv("ZIP_PATH")

# Инициализируем Retriever
retriever = Retriever(ZIP_PATH)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

pattern = "^[A-Za-zА-Яа-я0-9_]+.zip$"


# Функция для проверки наличия файлов авторизации и создания их,
# если они не существуют
def check_auth_files():
    for file_name in [USERS_FILE, ADMINS_FILE]:
        if not os.path.exists(file_name):
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['telegram_id', 'username'])


# Функция для регистрации пользователя
def register_user(telegram_id, username):
    with open(USERS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([telegram_id, username])


# Функция для проверки, зарегистрирован ли пользователь
def is_user_registered(telegram_id):
    with open(USERS_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['telegram_id']) == telegram_id:
                return True
    return False


# Функция для проверки, зарегистрирован ли админ
def is_admin_registered(telegram_id):
    with open(ADMINS_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['telegram_id']) == telegram_id:
                return True
    return False


# Функция для преобразования словаря в строку
def answer_to_message(answer: dict) -> str:
    text = answer['text']
    url = answer['url']
    department = answer['department']
    full_html_name = answer['full_html_name']
    return f"{text}\n\nОтдел: {department}\n{full_html_name}\n{url}"


# Декоратор для обработки команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Привет, я телеграм-бот ПЭК,чем могу помочь?")
    bot.reply_to(
        message, "Напиши /add_doc для обновления \
        базы данных документов.")
    bot.reply_to(
        message, "Команда: /add_user <telegram_id> <username> - \
        добавление нового пользователя админом.")


# Декоратор для обработки команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    if is_user_registered(user_id):
        bot.reply_to(message, f"Привет {username}, вы успешно авторизованы.")
    else:
        bot.reply_to(
            message, f"{username}, обратитесь к администратору \
            для регистрации.")


# Декоратор для обработки команды /add_user
@bot.message_handler(commands=['add_user'])
def handle_add_user(message):
    user_id = message.from_user.id
    if not is_admin_registered(user_id):
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    try:
        _, new_user_id, new_username = message.text.split()
        new_user_id = int(new_user_id)
        if is_user_registered(new_user_id):
            bot.reply_to(message, "Пользователь уже зарегистрирован.")
        else:
            register_user(new_user_id, new_username)
            bot.reply_to(message, f"Пользователь {
                         new_username} успешно добавлен.")
    except ValueError:
        bot.reply_to(
            message, "Неверный формат. Используйте\
            /add_user <telegram_id> <username>")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")


# Декоратор для обработки команды /add_doc
@bot.message_handler(commands=['add_doc'])
def handle_add_doc(message):
    bot.reply_to(message, "Напиши имя файла в формате filename.zip")
    if re.match(pattern, message.text):
        retriever.add_doc(f"data/{message.text}")
        bot.reply_to(message, "База данных обновлена")
    else:
        bot.reply_to(message, "Неверное имя файла")


# Текстовый обработчик
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text and is_user_registered(message.from_user.id):
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
    else:
        bot.send_message(
            message, "Обратитесь к администратору для регистрации.")


# Проверяем наличие файлы авторизации
check_auth_files()


# Запускаем бота
if __name__ == '__main__':
    print("Bot is ready...")
    bot.polling(none_stop=True, interval=0)
