import streamlit as st
import google.generativeai as genai
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union
import requests
from bs4 import BeautifulSoup

class ChatHandler:
    def __init__(self):
        """Initialize chat handler with necessary configurations."""
        self.chat_history = []
        self.context = {}
        self.load_config()
        
    def load_config(self):
        """Load API configurations from Streamlit secrets."""
        try:
            self.google_api_key = st.secrets["google"]["api_key"]
            genai.configure(api_key=self.google_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            logging.error(f"Error loading API configuration: {str(e)}")

    def chat_ui(self):
        """Display the chat interface in Streamlit."""
        st.markdown("### 💬 Interactive Chat Assistant")
        
        # Initialize session state for chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me anything about the document or legal matters..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                response = self.generate_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    def generate_response(self, prompt: str) -> str:
        """Generate a response based on the user's query."""
        try:
            # Analyze query type
            query_type = self._analyze_query_type(prompt)
            
            # Handle different types of queries
            if query_type == "document":
                return self._handle_document_query(prompt)
            elif query_type == "legal":
                return self._handle_legal_query(prompt)
            elif query_type == "real_world":
                return self._handle_real_world_query(prompt)
            else:
                return self._handle_general_query(prompt)
                
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def _analyze_query_type(self, prompt: str) -> str:
        """Analyze the type of query being asked."""
        # Document-related keywords
        doc_keywords = ["document", "text", "content", "paragraph", "section", "page", 
                       "analysis", "summary", "compare", "difference", "similar"]
                       
        # Legal-related keywords
        legal_keywords = ["law", "legal", "regulation", "compliance", "court", "judge", 
                         "case", "precedent", "statute", "right", "obligation"]
                         
        # Real-world keywords
        real_world_keywords = ["example", "real", "practice", "situation", "scenario", 
                             "case study", "industry", "business", "company"]

        # Count keyword matches
        doc_count = sum(1 for keyword in doc_keywords if keyword in prompt.lower())
        legal_count = sum(1 for keyword in legal_keywords if keyword in prompt.lower())
        real_count = sum(1 for keyword in real_world_keywords if keyword in prompt.lower())
        
        # Determine query type
        max_count = max(doc_count, legal_count, real_count)
        if max_count == 0:
            return "general"
        elif max_count == doc_count:
            return "document"
        elif max_count == legal_count:
            return "legal"
        else:
            return "real_world"

    def _handle_document_query(self, prompt: str) -> str:
        """Handle document-related queries."""
        try:
            # Get document context
            doc_context = st.session_state.get("extracted_text", "")
            
            # Prepare prompt for Gemini
            full_prompt = f"""You are a document analysis expert. Use the provided document context to answer questions accurately and comprehensively.

Document context: {doc_context}

Question: {prompt}"""
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            logging.error(f"Error handling document query: {str(e)}")
            return "I apologize, but I had trouble analyzing the document. Please try again."

    def _handle_legal_query(self, prompt: str) -> str:
        """Handle legal-related queries."""
        try:
            # Prepare prompt for Gemini
            full_prompt = f"""You are a legal expert assistant. Provide accurate legal information while noting that you cannot provide legal advice.

Question: {prompt}"""
            
            # Add relevant legal context if available
            if "legal_context" in st.session_state:
                full_prompt = f"Additional legal context: {st.session_state.legal_context}\n\n{full_prompt}"
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            return response.text + "\n\nNote: This information is for general understanding and should not be considered legal advice."
            
        except Exception as e:
            logging.error(f"Error handling legal query: {str(e)}")
            return "I apologize, but I had trouble processing your legal query. Please try again."

    def _handle_real_world_query(self, prompt: str) -> str:
        """Handle real-world scenario queries."""
        try:
            # Search for relevant real-world examples
            search_results = self._search_real_world_examples(prompt)
            
            # Prepare prompt for Gemini
            full_prompt = f"""You are an expert at analyzing real-world scenarios and providing practical insights.

Context from real-world examples: {search_results}

Question: {prompt}"""
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            logging.error(f"Error handling real-world query: {str(e)}")
            return "I apologize, but I had trouble finding relevant real-world examples. Please try again."

    def _handle_general_query(self, prompt: str) -> str:
        """Handle general queries."""
        try:
            # Prepare prompt for Gemini
            full_prompt = f"""You are a helpful assistant with expertise in document analysis and legal matters.

Question: {prompt}"""
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            logging.error(f"Error handling general query: {str(e)}")
            return "I apologize, but I had trouble processing your query. Please try again."

    def _search_real_world_examples(self, query: str) -> str:
        """Search for relevant real-world examples."""
        try:
            # Use web search to find relevant examples
            search_query = f"real world example case study {query}"
            
            # Perform web search and extract relevant information
            # This is a placeholder - implement actual web search functionality
            results = "Example real-world cases and studies related to the query..."
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching real-world examples: {str(e)}")
            return ""

    def save_chat_history(self):
        """Save chat history to session state."""
        if self.chat_history:
            st.session_state.chat_history = self.chat_history

    def load_chat_history(self):
        """Load chat history from session state."""
        if "chat_history" in st.session_state:
            self.chat_history = st.session_state.chat_history 