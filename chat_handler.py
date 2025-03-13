import streamlit as st
import logging
from google.generativeai import GenerativeModel
from typing import Optional, List, Dict

class ChatHandler:
    def __init__(self):
        """Initialize chat handler with Gemini model."""
        try:
            self.model = GenerativeModel("gemini-1.5-flash-latest")
        except Exception as e:
            logging.error(f"Error initializing Gemini model: {str(e)}")
            self.model = None

    def chat_with_document(self, document_text: str, user_query: str) -> Optional[str]:
        """Process user query about the document using Gemini."""
        if not document_text or not user_query or not self.model:
            return None

        try:
            # Create a prompt that includes document context and user query
            prompt = (
                "You are a legal document assistant. Based on the following document text, "
                "please answer the user's question accurately and professionally. "
                "If the answer cannot be found in the document, say so clearly.\n\n"
                f"Document text:\n{document_text[:10000]}\n\n"  # Limit text length
                f"User question: {user_query}"
            )
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response and hasattr(response, "text") else None
            
        except Exception as e:
            logging.error(f"Error in chat processing: {str(e)}")
            return f"Error processing your question: {str(e)}"

    def chat_ui(self) -> None:
        """Handle chat UI and functionality."""
        st.subheader("Chat with Document")
        
        if not st.session_state.get("extracted_text"):
            st.info("Please upload a document in the Upload tab first.")
            return
            
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["message"])
            elif message["role"] == "assistant":
                st.chat_message("assistant").write(message["message"])
        
        # Chat input
        user_message = st.chat_input("Ask a question about your document...")
        if user_message:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "message": user_message})
            
            # Process the query
            with st.spinner("🤖 Processing your question..."):
                response = self.chat_with_document(st.session_state.extracted_text, user_message)
                
                if response:
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "message": response})
                else:
                    st.error("Sorry, I couldn't process your question. Please try again.") 