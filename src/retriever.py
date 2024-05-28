import os
import shutil
from tqdm import tqdm
from bs4 import BeautifulSoup

from langchain_core.documents.base import Document
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings
)
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline, EmbeddingsFilter
)
from langchain.retrievers import ContextualCompressionRetriever

from src.data_loader import DataLoader

import time


class Retriever():
    def __init__(
            self,
            dataset: DataLoader,
            embedding_model: str = 'cointegrated/LaBSE-en-ru',
            vectorstore_dir: str = 'chroma',
            similarity_threshold: float = 0.4,
            retriever_search_type: str = 'mmr'
    ) -> None:
        self.dataset = dataset
        self.docs = self.create_docs()
        self.embedding = SentenceTransformerEmbeddings(
            model_name=embedding_model
        )
        self.vectorstore_dir = vectorstore_dir
        self.vectorstore = self.create_vectorstore()
        self.similarity_threshold = similarity_threshold
        self.retriever_search_type = retriever_search_type
        self.pipeline_compressor = self.create_pipeline_compressor()
        self.retriever = self.create_retriever()

    def answer(self, question: str) -> dict:
        """
        This Python function takes a question as input, retrieves relevant
        documents, extracts specific
        information from the top document, and returns a dictionary containing
        the text, URL, and
        department of the document.

        :param question: The `answer` function takes a question as input and
        returns a dictionary
        containing information related to the question. The information
        includes the text content of a
        document, the URL of the document, and the department to which the
        document belongs
        :type question: str
        :return: The function `answer` takes a question as input and returns a
        dictionary containing the
        text, URL, and department information related to the retrieved
        document.
        """
        compressed_docs = self.retriever.invoke(question)
        # doc = compressed_docs[0]
        # text = doc.page_content
        # url = doc.metadata['url']
        # department = doc.metadata['department']

        return compressed_docs

    def get_wiki_content(self, file: dict) -> str:
        """
        The function `get_wiki_content` reads HTML content from a file,
        extracts specific div elements,
        adds a title, and returns the text content.

        :param file: The `file` parameter is expected to be a dictionary
        containing information about
        the file to be processed. It should have at least two keys:
        :type file: dict
        :return: The function `get_wiki_content` returns the content of a
        specific HTML element (div)
        from a file specified in the input dictionary. It first reads the HTML
        content from the file,
        then uses BeautifulSoup to parse the HTML. It looks for a div element
        with class 'wiki-content',
        and if not found, it looks for a div element with class 'qa-info
        qa-info-detail'. Finally,
        """
        with open(file['source'], 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        div = soup.find('div', class_='wiki-content')
        if not div:
            div = soup.find('div', class_='qa-info qa-info-detail')

        # Add title and return content
        return file['name'] + '\n' + div.get_text()

    def create_docs(self) -> list[Document]:
        """
        The function `create_docs` generates a list of `Document` objects by
        extracting content from
        HTML files in a dataset.
        :return: A list of Document objects is being returned.
        """
        docs = []
        print("Creating document corpus from html files...")
        for file in tqdm(self.dataset):
            content = self.get_wiki_content(file)
            doc = Document(page_content=content, metadata=file)
            docs.append(doc)
        return docs

    def create_vectorstore(self) -> Chroma:
        """
        The function `create_vectorstore` deletes the old vectorstore if it
        exists and then creates a
        new vectorstore using Chroma from the provided documents and embedding.
        :return: The `create_vectorstore` method returns a `Chroma` object,
        which is created using the
        `Chroma.from_documents` method with the specified parameters.
        """
        start_time = time.time()
        # Remove old vectorstore if it exists
        if os.path.exists(self.vectorstore_dir):
            shutil.rmtree(self.vectorstore_dir)
            print("Old vectorstore has been deleted.")

        # Create vectorstore
        print("Creating a vectorstore...")
        vectordb = Chroma.from_documents(
            documents=self.docs,
            embedding=self.embedding,
            persist_directory=self.vectorstore_dir
        )
        end_time = time.time()
        execution_time = end_time - start_time
        print("Done creating a vectorstore...")
        print(f"Execution time: {execution_time} seconds")
        return vectordb

    def create_pipeline_compressor(self) -> DocumentCompressorPipeline:
        """
        The function `create_pipeline_compressor` creates a document
        compressor pipeline with text
        splitting, redundant filtering, and relevant filtering transformers.
        :return: The `create_pipeline_compressor` method returns a
        `DocumentCompressorPipeline` object
        that consists of a pipeline with three transformers:
        `RecursiveCharacterTextSplitter`,
        `EmbeddingsRedundantFilter`, and `EmbeddingsFilter`.
        """
        splitter = RecursiveCharacterTextSplitter(
            # chunk_size=300,
            chunk_overlap=0,
            separators=['\n\n', '\n', '. ']
        )
        redundant_filter = EmbeddingsRedundantFilter(embeddings=self.embedding)
        relevant_filter = EmbeddingsFilter(
            embeddings=self.embedding,
            similarity_threshold=self.similarity_threshold
        )
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, redundant_filter, relevant_filter]
        )
        return pipeline_compressor

    def create_retriever(self) -> ContextualCompressionRetriever:
        """
        The function `create_retriever` returns a
        `ContextualCompressionRetriever` object with specified
        base compressor and retriever.
        :return: The `create_retriever` method returns an instance of the
        `ContextualCompressionRetriever` class.
        """
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.pipeline_compressor,
            base_retriever=self.vectorstore.as_retriever(
                search_type=self.retriever_search_type)
        )
        return compression_retriever
