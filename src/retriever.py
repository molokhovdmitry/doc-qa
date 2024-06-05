import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import zipfile

from langchain_core.documents.base import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
            similarity_threshold: float = 0.3,
            retriever_search_type: str = 'mmr'
            ) -> None:
        self.zip_path = zip_path
        self.vectorstore_dir = vectorstore_dir
        self.retriever_search_type = retriever_search_type
        self.embedding = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        self.vectorstore = self.create_vectorstore()
        self.similarity_threshold = similarity_threshold
        # Pipeline to compress retrieved document splits
        self.pipeline_compressor = self.create_pipeline_compressor()
        self.retriever = self.create_retriever()

    def answer(self, question: str) -> dict:
        """Returns an answer dictionary to the question."""
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
        wiki_content = div.get_text('\n', strip=True)
        return wiki_content

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
        raw_docs = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print("Creating the document corpus from the zip archive...")
            for filename in tqdm(zip_ref.namelist()):
                if filename.split('.')[-1] == 'html':
                    name = filename.split('/')[-1][:-5]
                    html_content = zip_ref.read(filename).decode()
                    wiki_content = self.get_wiki_content(html_content)
                    wiki_content = name + wiki_content
                    url = self.get_confluence_url(html_content)
                    metadata = {
                        'name': name,
                        'full_html_name': filename,
                        'department': filename.split('/')[0],
                        'url': url
                    }
                    doc = Document(
                        page_content=wiki_content,
                        metadata=metadata
                    )
                    raw_docs.append(doc)

        # Split the documents into chunks
        doc_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
            separators=["\n\n", "\n", r"(?<=\. )", " "]
        )
        print("Splitting the documents into chunks...")
        docs = doc_splitter.split_documents(raw_docs)
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
                f"Loaded the vectorstore from /{self.vectorstore_dir}",
                f"with {doc_count} document splits."
            )
        else:
            docs = self.create_docs(self.zip_path)
            # Create vectorstore
            print("Creating a vectorstore...")
            vectordb = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding,
                persist_directory=self.vectorstore_dir
            )
            doc_count = vectordb._collection.count()
            print(
                f"Created a vectorstore in `{self.vectorstore_dir}`",
                f"with {doc_count} document splits."
            )
        return vectordb

    def add_documents(self, zip_path: str) -> None:
        """Updates the vectorstore with new documents from a zip archive."""
        doc_count = self.vectorstore._collection.count()
        print(f"Current document split count: {doc_count}")
        docs = self.create_docs(zip_path)
        print("Adding documents to the vectorstore...")
        self.vectorstore.add_documents(docs)
        doc_count = self.vectorstore._collection.count()
        print(f"Documents added. New document split count: {doc_count}")

    def create_pipeline_compressor(self) -> DocumentCompressorPipeline:
        """
        Create a compressor pipeline to split and filter
        retrieved document splits.
        """
        chunk_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", r"(?<=\. )", " "]
        )
        relevant_filter = EmbeddingsFilter(
            embeddings=self.embedding,
            similarity_threshold=self.similarity_threshold
        )

        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[chunk_splitter, relevant_filter]
        )
        return pipeline_compressor

    def create_retriever(self) -> ContextualCompressionRetriever:
        """Create a vectorstore retriever that will answer questions."""
        base_retriever = self.vectorstore.as_retriever(
            search_type=self.retriever_search_type,
            search_kwargs={
                'fetch_k': 20,
                'k': 15
            }
        )
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.pipeline_compressor,
            base_retriever=base_retriever
        )
        return compression_retriever
