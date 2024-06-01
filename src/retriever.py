import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import zipfile

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


class Retriever():
    def __init__(
            self,
            zip_path: str = 'data/data.zip',
            embedding_model: str = 'cointegrated/LaBSE-en-ru',
            vectorstore_dir: str = 'chroma',
            similarity_threshold: float = 0.25,
            retriever_search_type: str = 'mmr'
            ) -> None:
        self.zip_path = zip_path
        self.vectorstore_dir = vectorstore_dir
        self.similarity_threshold = similarity_threshold
        self.retriever_search_type = retriever_search_type
        self.embedding = SentenceTransformerEmbeddings(
            model_name=embedding_model
        )
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

    def get_wiki_content(self, html_content: str) -> str:
        """Returns wiki content from html content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        div = soup.find('div', class_='wiki-content')
        if not div:
            div = soup.find('div', class_='qa-info qa-info-detail')
        return div.get_text()

    def get_confluence_url(self, html_content: str) -> str:
        """Returns a confluence url from html file content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        link_element = soup.find('link', rel='canonical')
        if not link_element:
            return None
        url = link_element['href']
        return url

    def create_docs(self, zip_path) -> list[Document]:
        """Create documents from html files in a zip archive."""
        docs = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print("Creating the document corpus from the zip archive...")
            for filename in tqdm(zip_ref.namelist()):
                if filename.split('.')[-1] == 'html':
                    html_content = zip_ref.read(filename).decode()
                    wiki_content = self.get_wiki_content(html_content)
                    url = self.get_confluence_url(html_content)
                    metadata = {
                        'name': filename.split('/')[-1][:-5],
                        'full_html_name': filename,
                        'department': filename.split('/')[0],
                        'url': url
                    }
                    doc = Document(
                        page_content=wiki_content,
                        metadata=metadata
                    )
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
            doc_count = vectordb._collection.count()
            print(
                f"Loaded vectorstore from {self.vectorstore_dir}",
                f"with {doc_count} documents."
            )
        else:
            docs = self.create_docs(self.zip_path)
            # Create vectorstore
            print("Creating the vectorstore...")
            vectordb = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding,
                persist_directory=self.vectorstore_dir
            )
            doc_count = vectordb._collection.count()
            print(
                f"Created vectorstore in {self.vectorstore_dir}",
                f"with {doc_count} documents."
            )
        return vectordb

    def add_documents(self, zip_path: str) -> None:
        """Updates the vectorstore with new documents from a zip archive."""
        doc_count = self.vectorstore._collection.count()
        print(f"Current document count: {doc_count}")
        docs = self.create_docs(zip_path)
        print("Adding documents to the vectorstore...")
        self.vectorstore.add_documents(docs)
        doc_count = self.vectorstore._collection.count()
        print(f"Documents added. New document count: {doc_count}")

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
