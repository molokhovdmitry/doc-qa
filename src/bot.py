from dotenv import load_dotenv
import telebot
import os
import csv

from src.retriever import Retriever


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

help_string = """Введите любой запрос к данным.

# Вывести помощь.
/help

# Добавить к векторному хранилищу документы из zip архива.
# Требуются права администратора.
/add_docs <path/to/file.zip>
/add_docs data/data.zip

# Добавить пользователя
# Требуются права администратора.
/add_user <telegram_id> <username>
/add_user 6385486588 molokhovdmitry
"""


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
    bot.send_message(
        message.from_user.id,
        help_string)


# Декоратор для обработки команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    if is_user_registered(user_id) or is_admin_registered(user_id):
        bot.send_message(
            user_id,
            f"Привет {username}, вы успешно авторизованы."
        )
    else:
        bot.send_message(
            user_id,
            f"{username}, обратитесь к администратору для регистрации.\n" +
            f"Ваш Telegram ID: {user_id}"
        )


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
            bot.reply_to(
                message, f"Пользователь {new_username} успешно добавлен.")
    except ValueError:
        bot.reply_to(
            message, "Неверный формат. Используйте\
            /add_user <telegram_id> <username>")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")


# Декоратор для обработки команды /add_docs
@bot.message_handler(commands=['add_docs'])
def handle_add_docs(message):
    zip_path = message.text.split()[-1]
    if not os.path.exists(zip_path):
        bot.send_message(
            message.from_user.id,
            f"Файл {zip_path} не найден."
        )
        return
    if zip_path.split('.')[-1] == 'zip':
        bot.send_message(
            message.from_user.id,
            "Обновляю хранилище..."
        )
        retriever.add_documents(zip_path)
        bot.send_message(
            message.from_user.id,
            "Векторное хранилище обновлено."
        )
    else:
        bot.send_message(
            message.from_user.id,
            "Файл не является .zip архивом."
        )


# Текстовый обработчик
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id
    registered = is_user_registered(user_id) or is_admin_registered(user_id)
    if message.text and registered:
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
            message.from_user.id,
            "Обратитесь к администратору для регистрации."
        )


# Проверяем наличие файлы авторизации
check_auth_files()

# Запускаем бота
if __name__ == '__main__':
    print("Bot is ready...")
    bot.polling(none_stop=True, interval=0)
