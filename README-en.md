# doc-qa
🇷🇺 [Русский](README.md)

Telegram bot for searching documents using `LangChain`. Developed for a hackathon for data under NDA.

## How it works
### Parsing `html`
All the necessary content is located in a `div` element with the class `wiki-content` (one exception out of 840 pages). We also extract the link for `Confluence` from the `html` file, so we don't use the provided `txt` files. The data is extracted using `BeautifulSoup`.

### `LangChain`
1. The developed `Retriever` class takes the path to a `zip` archive, reads `html` files from it, and creates a list of documents of the class [`langchain_core.documents.base.Document`](https://api.python.langchain.com/en/latest/documents/langchain_core.documents.base.Document.html). Each document has `page_content` and `metadata`. We load the `wiki-content` of the page into `page_content` and the extracted link, `html` file name, and department name into `metadata`.
2. The obtained documents are split into fragments using one of the [Text Splitters](https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers), in our case [`RecursiveCharacterTextSplitter`](https://api.python.langchain.com/en/latest/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html).
3. Using the vector representation model [`cointegrated/LaBSE-en-ru`](https://huggingface.co/cointegrated/LaBSE-en-ru), a `Chroma` [vector store](https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores) is created from the text fragments.
4. Using the `Maximal Marginal Relevance` method, the top `k` fragments most similar to the given query are found. These fragments are then processed by [`DocumentCompressorPipeline`](https://api.python.langchain.com/en/latest/retrievers/langchain.retrievers.document_compressors.base.DocumentCompressorPipeline.html), consisting of another [`RecursiveCharacterTextSplitter`](https://api.python.langchain.com/en/latest/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html) to split the fragments into even smaller fragments, and [`EmbeddingsFilter`](https://api.python.langchain.com/en/latest/retrievers/langchain.retrievers.document_compressors.embeddings_filter.EmbeddingsFilter.html) to select the most relevant fragments.

### Bot
The bot has a basic authentication system and a command to add new documents to the vector store. Admin or user role is required for usage. Administrators are manually added to `data/admins.csv`, which is created after the bot is launched. Users can be added with the command `/add_user <telegram_id> <username>`.

#### Bot commands
```
# Display help.
/help

# Add documents from a zip archive to the vector store.
# Admin rights required.
/add_docs <path/to/file.zip>
/add_docs data/data.zip

# Add a user
# Admin rights required.
/add_user <telegram_id> <username>
/add_user 6385486588 molokhovdmitry
```

### Suggestions for improvements and customization
- The main direction for improvement is using one of the LLMs [implemented in `LangChain`](https://python.langchain.com/v0.1/docs/integrations/chat/). LLM can be used at the question-answering stage, where the fragments obtained with [`DocumentCompressorPipeline`](https://api.python.langchain.com/en/latest/retrievers/langchain.retrievers.document_compressors.base.DocumentCompressorPipeline.html) are used by the model as content for answering the question. You can also use [text embedding functions](https://python.langchain.com/v0.1/docs/integrations/text_embedding/) of these models when creating the vector store.
- Choosing other types of splitters and filters.
- Changing `chunk_size`, `chunk_overlap`, and `separators` parameters of the splitters.
- Choosing another [`Retriever`](https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/) instead of `Vectorstore`.
- Choosing another search method instead of `Maximum Marginal Relevance`.
- Changing [parameters](https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/vectorstore/) `fetch_k`, `k`, and `lambda_mult` for the search method.

## PEС Data
To use the project with PEС data, download all provided files as a `zip` archive, rename the archive to `data.zip`, place it in the repository's `data` folder, and follow the installation and launch instructions.

## Installation and launch
```
git clone https://github.com/molokhovdmitry/doc-qa
cd doc-qa
```
Rename the `.env.example` file to `.env` and specify the Telegram bot token and the path to the data archive.

Install the dependencies:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Launch the bot:
```
python -m src.bot
```
Enter your Telegram ID and username in `admins.csv` for access to all bot commands.

## Limitations and optimization
For creating the vector store and answering a large number of questions, a GPU is recommended.

To speed up the creation of the vector store, you can increase `chunk_size` and decrease `chunk_overlap` of the `RecursiveCharacterTextSplitter` used for the initial document splitting.

To speed up the question-answering process, you can decrease the `fetch_k` and `k` parameters of the search method.