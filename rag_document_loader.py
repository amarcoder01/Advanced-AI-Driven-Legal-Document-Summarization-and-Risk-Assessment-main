"""
Document loading and processing module.
"""
import os
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from rag_config import CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENT_DIR

class DocumentProcessor:
    """Handles document loading and preprocessing for RAG."""
    
    def __init__(self, document_dir: Optional[str] = None):
        """Initialize the document processor.
        
        Args:
            document_dir: Directory containing documents to process
        """
        self.document_dir = document_dir or DOCUMENT_DIR
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
    def _get_loader(self, file_path: str):
        """Get the appropriate loader based on file extension."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return PyPDFLoader(file_path)
        elif file_extension == '.txt':
            return TextLoader(file_path)
        elif file_extension == '.csv':
            return CSVLoader(file_path)
        elif file_extension in ['.md', '.markdown']:
            return UnstructuredMarkdownLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load and split a single document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of document chunks
        """
        loader = self._get_loader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def load_documents(self, directory: Optional[str] = None) -> List[Document]:
        """Load all documents from a directory.
        
        Args:
            directory: Directory containing documents (defaults to self.document_dir)
            
        Returns:
            List of document chunks
        """
        directory = directory or self.document_dir
        all_documents = []
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created document directory: {directory}")
            return all_documents
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    document_chunks = self.load_document(file_path)
                    all_documents.extend(document_chunks)
                    print(f"Loaded {len(document_chunks)} chunks from {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return all_documents 