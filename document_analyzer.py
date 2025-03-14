import streamlit as st
import logging
import google.generativeai as genai
from typing import Optional
import os

class DocumentAnalyzer:
    def __init__(self):
        """Initialize the document analyzer with Gemini model."""
        try:
            # Try getting API key from environment variable first
            api_key = os.getenv('GOOGLE_API_KEY')
            
            # If not in environment, try Streamlit secrets
            if not api_key:
                try:
                    # Try the new location first
                    api_key = st.secrets["api"]["GEMINI_API_KEY"]
                except:
                    try:
                        # Try the old location as fallback
                        api_key = st.secrets["google"]["api_key"]
                    except:
                        pass
            
            # If still no API key, show error
            if not api_key:
                st.error("Google API key not found. Please set it in your environment variables as 'GOOGLE_API_KEY' or in Streamlit secrets.")
                self.model = None
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
        except Exception as e:
            logging.error(f"Error initializing Gemini model: {str(e)}")
            st.error(f"Error initializing document analyzer: {str(e)}")
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
            if not response or not response.text:
                raise ValueError("Empty response received from the model")
                
            return response.text.strip()
            
        except Exception as e:
            logging.error(f"Error in document summarization: {str(e)}")
            st.error(f"Error generating summary: {str(e)}")
            return None

    def analyze_document_ui(self) -> None:
        """Handle document analysis UI and functionality."""
        st.subheader("Document Analysis")
        
        if st.session_state.get("extracted_text"):
            if st.button("Generate Summary", key="generate_summary_button"):
                with st.spinner("Analyzing document..."):
                    summary = self.summarize_document(st.session_state.extracted_text)
                    if summary:
                        st.session_state.summary = summary
                        st.success("Summary generated successfully!")
                    else:
                        st.error("Failed to generate summary. Please check your API key configuration and try again.")
            
            if st.session_state.get("summary"):
                st.markdown("### 📝 Document Summary")
                st.write(st.session_state.summary)
        else:
            st.info("Please upload a document in the Upload tab first.") 
