"""
Configuration settings for the RAG integration.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import streamlit if available
try:
    import streamlit as st
    USING_STREAMLIT = True
except ImportError:
    USING_STREAMLIT = False

# API Keys - Check both Streamlit secrets and environment variables
if USING_STREAMLIT:
    try:
        # Get from Streamlit secrets api section
        GOOGLE_API_KEY = st.secrets.api.GOOGLE_API_KEY
        HUGGINGFACE_API_KEY = st.secrets.api.HUGGINGFACE_API_KEY
    except:
        # Fallback to environment variables
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
else:
    # Get from environment variables
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Set Hugging Face token for the hub if available
if HUGGINGFACE_API_KEY:
    os.environ["HUGGINGFACE_TOKEN"] = HUGGINGFACE_API_KEY

# Model settings
GEMINI_MODEL = "gemini-pro"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RETRIEVAL = 5

# Vector database settings
VECTOR_DB_PATH = "./vector_db"

# Document settings
DOCUMENT_DIR = "./documents" 