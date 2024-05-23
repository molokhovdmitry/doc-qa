# doc-qa
🇷🇺 [Русский](README.md)

Telegram bot for document information retrieval with `LangChain`. Made within the hackathon for data under NDA.

## PEC data
To use the project with PEC data, download all the files in a `zip` file, rename the archive to `data.zip` and move it to `data` folder of the repository.

## Other data
<details>

To use the bot on different data `Retriever` object should receive the object with `__getitem__` and `__len__` methods that yields a dictionaries with the following keys:

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

## Installation and running
```
git clone https://github.com/molokhovdmitry/doc-qa
cd doc-qa
```
Rename `.env.example` to `.env` and set the bot token.
```
pip install -r requirements.txt
python -m src.bot
```
