"""
Google Gemini model integration with LangChain.
"""
import os
from typing import List, Dict, Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from rag_config import GOOGLE_API_KEY, GEMINI_MODEL, TOP_K_RETRIEVAL

# Default prompt templates
DEFAULT_PROMPT_TEMPLATE = """
You are a helpful AI assistant that provides accurate and detailed information.
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say you don't know. Don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:
"""

class GeminiLangChain:
    """Integrates Google's Gemini model with LangChain for RAG."""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.2):
        """Initialize the Gemini LangChain integration.
        
        Args:
            model_name: Name of the Gemini model to use
            temperature: Model temperature (0.0 to 1.0)
        """
        if not GOOGLE_API_KEY:
            raise ValueError("Google API Key not found. Please set it in your environment or Streamlit secrets.")
            
        self.model_name = model_name or GEMINI_MODEL
        self.temperature = temperature
        
        # Initialize the Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            convert_system_message_to_human=True,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Default prompt
        self.prompt = PromptTemplate(
            template=DEFAULT_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = None
        self.retrieval_qa = None
    
    def setup_qa_chain(self, chain_type: str = "stuff"):
        """Set up a question answering chain.
        
        Args:
            chain_type: Chain type (stuff, map_reduce, refine, map_rerank)
            
        Returns:
            The QA chain
        """
        self.qa_chain = load_qa_chain(
            llm=self.llm,
            chain_type=chain_type,
            prompt=self.prompt
        )
        return self.qa_chain
    
    def setup_retrieval_qa(self, vector_store, chain_type: str = "stuff"):
        """Set up a retrieval QA chain.
        
        Args:
            vector_store: Vector store for document retrieval
            chain_type: Chain type (stuff, map_reduce, refine, map_rerank)
            
        Returns:
            The Retrieval QA chain
        """
        self.retrieval_qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=chain_type,
            retriever=vector_store.as_retriever(search_kwargs={"k": TOP_K_RETRIEVAL}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
        return self.retrieval_qa
    
    def answer_with_sources(self, query: str, documents: List[Document] = None):
        """Answer a question with source documents.
        
        Args:
            query: User's question
            documents: List of documents (if not using retrieval QA)
            
        Returns:
            Answer and source documents
        """
        if documents and self.qa_chain:
            # Use the QA chain with provided documents
            result = self.qa_chain(
                {"input_documents": documents, "question": query},
                return_only_outputs=False
            )
            return {
                "answer": result["output_text"],
                "source_documents": documents
            }
        elif self.retrieval_qa:
            # Use the retrieval QA chain
            result = self.retrieval_qa({"query": query})
            return {
                "answer": result["result"],
                "source_documents": result["source_documents"]
            }
        else:
            raise ValueError("Either provide documents or set up a retrieval QA chain first.") 