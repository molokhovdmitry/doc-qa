# doc-qa
🇬🇧 [English](README-en.md)

Телеграм бот для поиска по документам с помощью `LangChain`. Сделан в рамках хакатона для данных, находящихся под NDA.

## Как работает
### Парсинг `html`
Весь необходимый нам контент находится в элементе `div` с классом `wiki-content` (одно исключение из 840 страниц). Также из `html` файла можно извлечь ссылку для `Confluence`, из-за чего мы не используем предоставленные `txt` файлы. Данные извлекаем с помощью `BeautifulSoup`.

### `LangChain`
1. Разработанный класс `Retriever` получает на вход путь к `zip` архиву, из которого считывает `html` файлы и создаёт список документов класса [`langchain_core.documents.base.Document`](https://api.python.langchain.com/en/latest/documents/langchain_core.documents.base.Document.html). У каждого документа есть `page_content` и `metadata`. В `page_content` мы загружаем `wiki-content` страницы, в `metadata` загружаем извлеченную ссылку, название `html` файла и название отдела.
2. Из полученных документов создаются фрагменты документов с помощью одного из 
[Text Splitters](https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers), в нашем случае [`RecursiveCharacterTextSplitter`](https://api.python.langchain.com/en/latest/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html).
3. Из фрагментов текстов с помощью модели векторного представления [`cointegrated/LaBSE-en-ru`](https://huggingface.co/cointegrated/LaBSE-en-ru) создаётся [векторное хранилище](https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores) `Chroma`.
4. По методу `Maximal Marginal Relevance` находятся топ `k` похожих на заданный вопрос фрагментов, после чего эти фрагменты обрабатываются [`DocumentCompressorPipeline`](https://api.python.langchain.com/en/latest/retrievers/langchain.retrievers.document_compressors.base.DocumentCompressorPipeline.html), состоящим из еще одного [`RecursiveCharacterTextSplitter`](https://api.python.langchain.com/en/latest/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html) и из [`EmbeddingsFilter`](https://api.python.langchain.com/en/latest/retrievers/langchain.retrievers.document_compressors.embeddings_filter.EmbeddingsFilter.html) который выбирает из еще более мелких фрагментов наиболее релевантные.

### Бот
В боте реализована простейшая система авторизации и команда для добавления новых документов в векторное хранилище. Для использования необходима роль администратора либо пользователя. Администраторы добавляются вручную в `data/admins.csv`, созданный после запуска бота. Пользователей можно добавить командой `/add_user <telegram_id> <username>`.

#### Команды бота
```
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
```

### Предложения по улучшению и настройке
- Основным направлением для улучшения будет использование одной из LLM, [реализованных в `LangChain`](https://python.langchain.com/v0.1/docs/integrations/chat/). Можно использовать LLM на этапе ответа на вопрос, где полученные с помощью [`DocumentCompressorPipeline`](https://api.python.langchain.com/en/latest/retrievers/langchain.retrievers.document_compressors.base.DocumentCompressorPipeline.html) фрагменты используются моделью как контент для ответа на вопрос. Также можно использовать [функции векторного представления](https://python.langchain.com/v0.1/docs/integrations/text_embedding/) этих моделей при создании векторного хранилища.
- Выбор других типов сплиттеров и фильтров
- Изменение параметров `chunk_size`, `chunk_overlap` и `separators` сплиттеров.
- Выбор другого [`Retriever`](https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/) вместо `Vectorstore`.
- Выбор другого метода поиска вместо `Maximum Marginal Relevance`.
- Изменение [параметров](https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/vectorstore/) `fetch_k`, `k` и `lambda_mult` для метода поиска.

## Данные ПЭК
Для использования проекта с данными ПЭК, скачайте все предоставленные файлы `zip` архивом, переименуйте архив в `data.zip`, поместите его в папку `data` репозитория, далее следуйте инструкции по установке и запуску.

## Установка и запуск
```
git clone https://github.com/molokhovdmitry/doc-qa
cd doc-qa
```
Переименуйте файл `.env.example` в `.env`, укажите в нем токен для телеграм бота и путь к архиву с данными.

Установите зависимости:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Запустите бот:
```
python -m src.bot
```
Введите в `admins.csv` ваш Telegram ID и имя пользователя для доступа ко всем командам бота.

## Ограничения и оптимизация
Для создания векторного хранилища и ответа на большое количество вопросов рекомендуется наличие видеокарты.

Для увеличения скорости создания векторного хранилища можно повысить `chunk_size` и понизить `chunk_overlap` у `RecursiveCharacterTextSplitter`, который используется для первичного деления документов на фрагменты.

Для увеличения скорости ответа на вопрос можно понизить параметры `fetch_k`, и `k` метода поиска.
