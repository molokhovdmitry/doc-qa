import os
from tqdm import tqdm
from bs4 import BeautifulSoup

from langchain_core.documents.base import Document
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings
)
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline, EmbeddingsFilter
)
from langchain.retrievers import ContextualCompressionRetriever

from src.data_loader import DataLoader


class Retriever():
    def __init__(
            self,
            dataset: DataLoader,
            embedding_model: str = 'cointegrated/LaBSE-en-ru',
            vectorstore_dir: str = 'chroma',
            similarity_threshold: float = 0.25,
            retriever_search_type: str = 'mmr'
            ) -> None:
        self.dataset = dataset
        self.vectorstore_dir = vectorstore_dir
        self.similarity_threshold = similarity_threshold
        self.retriever_search_type = retriever_search_type
        self.embedding = SentenceTransformerEmbeddings(
            model_name=embedding_model
        )
        if not os.path.exists(self.vectorstore_dir):
            self.docs = self.create_docs()
        self.vectorstore = self.create_vectorstore()
        self.pipeline_compressor = self.create_pipeline_compressor()
        self.retriever = self.create_retriever()

    def answer(self, question: str) -> dict:
        compressed_docs = self.retriever.invoke(question)
        if len(compressed_docs) == 0:
            return None
        doc = compressed_docs[0]
        text = doc.page_content
        url = doc.metadata['url']
        full_html_name = doc.metadata['full_html_name']
        department = doc.metadata['department']

        answer = {
            'text': text,
            'url': url,
            'full_html_name': full_html_name,
            'department': department
        }

        return answer

    def get_wiki_content(self, file: dict) -> str:
        with open(file['source'], 'r') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        div = soup.find('div', class_='wiki-content')
        if not div:
            div = soup.find('div', class_='qa-info qa-info-detail')

        # Add title and return content
        return file['name'] + '\n' + div.get_text()

    def create_docs(self) -> list[Document]:
        docs = []
        print("Creating document corpus from html files...")
        for file in tqdm(self.dataset):
            content = self.get_wiki_content(file)
            doc = Document(page_content=content, metadata=file)
            docs.append(doc)
        return docs

    def create_vectorstore(self) -> Chroma:
        """Loads or creates a vectorstore."""
        if os.path.exists(self.vectorstore_dir):
            # Load vectorstore if it exists
            vectordb = Chroma(
                persist_directory=self.vectorstore_dir,
                embedding_function=self.embedding
            )
            print(f"Loaded vectorstore from {self.vectorstore_dir}.")
        else:
            # Create vectorstore
            print("Creating a vectorstore...")
            vectordb = Chroma.from_documents(
                documents=self.docs,
                embedding=self.embedding,
                persist_directory=self.vectorstore_dir
            )
        return vectordb

    def create_pipeline_compressor(self) -> DocumentCompressorPipeline:
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
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.pipeline_compressor,
            base_retriever=self.vectorstore.as_retriever(
                search_type=self.retriever_search_type)
        )
        return compression_retriever
