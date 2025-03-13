import streamlit as st
import logging
from google.generativeai import GenerativeModel
from typing import Optional

class DocumentAnalyzer:
    def __init__(self):
        """Initialize the document analyzer with Gemini model."""
        try:
            self.model = GenerativeModel("gemini-1.5-flash-latest")
        except Exception as e:
            logging.error(f"Error initializing Gemini model: {str(e)}")
            self.model = None

    def summarize_document(self, text: str) -> Optional[str]:
        """Generate a comprehensive summary of the document."""
        if not text or not self.model:
            return None

        try:
            # Limit text length to avoid token limit issues
            max_text_length = 10000
            text_to_analyze = text[:max_text_length]
            
            prompt = (
                "You are a legal document specialist. Analyze the following legal document text and provide an informative summary. "
                "Format your response in two clearly separated sections:\n\n"
                "1. DOCUMENT DESCRIPTION (first): A concise 2-3 sentence description of what this document is - identify the document type, "
                "its apparent purpose, and general subject matter.\n\n"
                "2. DOCUMENT SUMMARY (second): A well-organized summary of the key points using bullet points and subsections. "
                "Include the main clauses, provisions, rights, obligations, and any notable terms. Maintain a formal, factual tone. "
                "Use clear headings for different sections of the summary.\n\n"
                f"Document text:\n{text_to_analyze}"
            )
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response and hasattr(response, "text") else None
            
        except Exception as e:
            logging.error(f"Error in document summarization: {str(e)}")
            return None

    def analyze_document_ui(self) -> None:
        """Handle document analysis UI and functionality."""
        st.subheader("Document Analysis")
        
        if st.session_state.get("extracted_text"):
            if st.button("Generate Summary", key="generate_summary_button"):
                with st.spinner("Analyzing document..."):
                    summary = self.summarize_document(st.session_state.extracted_text)
                    st.session_state.summary = summary if summary else "No summary generated."
            
            if st.session_state.get("summary"):
                st.markdown("### 📝 Document Summary")
                st.write(st.session_state.summary)
        else:
            st.info("Please upload a document in the Upload tab first.") 