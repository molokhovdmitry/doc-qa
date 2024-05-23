# doc-qa
🇬🇧 [English](README-en.md)

Телеграм бот для поиска по документам с помощью `LangChain`. Сделан в рамках хакатона для данных, находящихся под NDA.

## Данные ПЭК
Для использования проекта с данными ПЭК, скачайте все предоставленные файлы `zip` архивом, переименуйте архив в `data.zip`, поместите его в папку `data` репозитория, далее следуйте инструкции по установке и запуску.

## Другие данные
<details>

При использовании бота для других данных, на вход объекта класса `Retriever` требуется подать объект, имеющий методы `__getitem__` и `__len__`, возвращающий при итерации словарь со следущими ключами:

```
{
    'source': 'path to html file',
    'name': 'actual file name without extension',
    'full_html_name': 'full file name',
    'department': 'department name',
    'url': 'url'
}
```
</details>

## Установка и запуск
```
git clone https://github.com/molokhovdmitry/doc-qa
cd doc-qa
```
Переименуйте файл `.env.example` в `.env`, укажите в нем токен для телеграм бота.
```
pip install -r requirements.txt
python -m src.bot
```
