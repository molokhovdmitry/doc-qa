# doc-qa
🇷🇺 [Русский](README.md)

Telegram bot for document information retrieval with `LangChain`. Made within the hackathon for data under NDA.

## PEC data
To use the project with PEC data, download all the files in a `zip` file, rename the archive to `data.zip` and move it to `data` folder of the repository.

## Installation and running
```
git clone https://github.com/molokhovdmitry/doc-qa
cd doc-qa
```
Rename `.env.example` to `.env` and set the bot token.
```
pip install -r requirements.txt
python -m spacy download ru_core_news_lg
python -m src.bot
```
