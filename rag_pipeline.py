"""
Main RAG pipeline that integrates all components.
"""
import os
from typing import List, Dict, Any, Optional

from rag_document_loader import DocumentProcessor
from rag_embeddings import EmbeddingManager
from rag_gemini_integration import GeminiLangChain
from rag_config import TOP_K_RETRIEVAL

class RAGPipeline:
    """Main RAG pipeline that integrates document processing, embeddings, and LLM."""
    
    def __init__(self, 
                document_dir: Optional[str] = None,
                vector_db_path: Optional[str] = None,
                embedding_model: Optional[str] = None,
                gemini_model: Optional[str] = None,
                temperature: float = 0.2):
        """Initialize the RAG pipeline.
        
        Args:
            document_dir: Directory containing documents
            vector_db_path: Directory to store vector database
            embedding_model: Hugging Face embedding model name
            gemini_model: Gemini model name
            temperature: Model temperature
        """
        # Initialize components
        self.document_processor = DocumentProcessor(document_dir)
        self.embedding_manager = EmbeddingManager(embedding_model, vector_db_path)
        self.gemini_langchain = GeminiLangChain(gemini_model, temperature)
        
        # Pipeline state
        self.documents = []
        self.is_initialized = False
    
    def initialize(self, force_reload: bool = False, store_type: str = "chroma"):
        """Initialize the RAG pipeline.
        
        Args:
            force_reload: Whether to force reload documents and recreate the vector store
            store_type: Type of vector store to use
            
        Returns:
            Self for method chaining
        """
        try:
            # Try to load existing vector store
            if not force_reload:
                self.embedding_manager.load_vector_store(store_type)
                self.gemini_langchain.setup_retrieval_qa(self.embedding_manager.vector_store)
                self.is_initialized = True
                print("Loaded existing vector store successfully.")
                return self
        except (FileNotFoundError, ValueError) as e:
            print(f"Could not load existing vector store: {e}")
            print("Creating new vector store...")
            
        # Load documents and create vector store
        self.documents = self.document_processor.load_documents()
        
        if not self.documents:
            print("No documents found. Please add documents to the documents directory.")
            return self
            
        print(f"Loaded {len(self.documents)} document chunks. Creating vector store...")
        self.embedding_manager.create_vector_store(self.documents, store_type)
        
        # Setup retrieval QA
        self.gemini_langchain.setup_retrieval_qa(self.embedding_manager.vector_store)
        
        self.is_initialized = True
        print("RAG pipeline initialized successfully.")
        return self
    
    def add_documents(self, file_paths: List[str], recreate_vector_store: bool = True, store_type: str = "chroma"):
        """Add new documents to the RAG pipeline.
        
        Args:
            file_paths: List of file paths to add
            recreate_vector_store: Whether to recreate the vector store
            store_type: Type of vector store to use
            
        Returns:
            Self for method chaining
        """
        new_documents = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                doc_chunks = self.document_processor.load_document(file_path)
                new_documents.extend(doc_chunks)
                print(f"Added {len(doc_chunks)} chunks from {file_path}")
            else:
                print(f"File not found: {file_path}")
        
        if new_documents:
            self.documents.extend(new_documents)
            
            if recreate_vector_store:
                self.embedding_manager.create_vector_store(self.documents, store_type)
                self.gemini_langchain.setup_retrieval_qa(self.embedding_manager.vector_store)
                print("Vector store recreated with new documents.")
                
        return self
    
    def query(self, query: str, k: int = None) -> Dict[str, Any]:
        """Query the RAG pipeline.
        
        Args:
            query: User query
            k: Number of documents to retrieve (overrides default)
            
        Returns:
            Dictionary with answer and source documents
        """
        if not self.is_initialized:
            raise ValueError("RAG pipeline not initialized. Call initialize() first.")
            
        k = k or TOP_K_RETRIEVAL
        
        # Option 1: Use the retrieval QA chain (preferred)
        if self.gemini_langchain.retrieval_qa:
            result = self.gemini_langchain.answer_with_sources(query)
            return result
            
        # Option 2: Manual retrieval and QA
        elif self.embedding_manager.vector_store:
            # Make sure QA chain is set up
            if not self.gemini_langchain.qa_chain:
                self.gemini_langchain.setup_qa_chain()
                
            # Retrieve relevant documents
            docs = self.embedding_manager.similarity_search(query, k=k)
            retrieved_docs = [doc[0] for doc in docs]  # Extract documents from (doc, score) tuples
            
            # Get answer
            result = self.gemini_langchain.answer_with_sources(query, retrieved_docs)
            return result
            
        else:
            raise ValueError("No vector store or QA chain available.") 