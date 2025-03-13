import streamlit as st

def initialize_session_state():
    """Initialize session state variables."""
    session_vars = {
        'extracted_text': None,
        'summary': None,
        'risks': None,
        'chat_history': [],
        'uploaded_docs': {},
        'main_doc_id': None,
        'summaries': {},
        'gdpr_consent': False,
        'show_gdpr_banner': True,
        'show_privacy_policy': False,
        'current_year': None
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

def reset_analysis_state():
    """Reset analysis-related state variables."""
    st.session_state.summary = None
    st.session_state.risks = None

def update_document_state(file_id, name, text, file_type):
    """Update state with new document information."""
    st.session_state.uploaded_docs[file_id] = {
        'name': name,
        'text': text,
        'type': file_type
    }
    
    if st.session_state.main_doc_id is None:
        st.session_state.main_doc_id = file_id 