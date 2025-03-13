"""
Embedding and vector store management module.
"""
from typing import List, Optional
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain.schema import Document

from rag_config import EMBEDDING_MODEL, VECTOR_DB_PATH, HUGGINGFACE_API_KEY

class EmbeddingManager:
    """Manages embeddings and vector storage for RAG."""
    
    def __init__(self, model_name: Optional[str] = None, persist_directory: Optional[str] = None):
        """Initialize the embedding manager.
        
        Args:
            model_name: Name of the Hugging Face embedding model
            persist_directory: Directory to store the vector database
        """
        self.model_name = model_name or EMBEDDING_MODEL
        self.persist_directory = persist_directory or VECTOR_DB_PATH
        
        # Initialize the embedding model
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}
        
        # Add API token if available
        if HUGGINGFACE_API_KEY:
            model_kwargs["token"] = HUGGINGFACE_API_KEY
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        self.vector_store = None
        
        # Ensure vector store directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
    
    def create_vector_store(self, documents: List[Document], store_type: str = "chroma"):
        """Create a vector store from documents.
        
        Args:
            documents: List of document chunks
            store_type: Type of vector store ("faiss" or "chroma")
            
        Returns:
            The vector store instance
        """
        if store_type.lower() == "faiss":
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            self.vector_store.save_local(self.persist_directory)
        else:  # Default to Chroma
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            self.vector_store.persist()
            
        return self.vector_store
    
    def load_vector_store(self, store_type: str = "chroma"):
        """Load a vector store from disk.
        
        Args:
            store_type: Type of vector store ("faiss" or "chroma")
            
        Returns:
            The vector store instance
        """
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Vector store directory not found: {self.persist_directory}")
            
        if store_type.lower() == "faiss":
            self.vector_store = FAISS.load_local(self.persist_directory, self.embeddings)
        else:  # Default to Chroma
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
        return self.vector_store
    
    def similarity_search(self, query: str, k: int = 5):
        """Perform similarity search on the vector store.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of documents and their similarity scores
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store or load_vector_store first.")
            
        return self.vector_store.similarity_search_with_score(query, k=k) 