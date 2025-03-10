"""
GDPR Compliance Module for AI Legal Document Assistant

This module provides GDPR compliance features for the Streamlit application:
1. Small, unobtrusive GDPR Consent Popup at the bottom of the screen
2. In-app Privacy Policy display using Markdown
3. GDPR Information via an external iframe

These features help ensure the application adheres to GDPR requirements for data protection.
"""

import streamlit as st
import os

# Define file paths and constants
PRIVACY_POLICY_FILE = "privacy_policy.html"
PRIVACY_POLICY_PATH = os.path.join(os.getcwd(), PRIVACY_POLICY_FILE)
GDPR_INFO_URL = "https://gdpr-info.eu/"

# Privacy policy content as Markdown for in-app display.
PRIVACY_POLICY_MARKDOWN = """
# Privacy Policy

## 1. Overview

Welcome to AI Legal Document Assistant. We are committed to protecting your privacy and handling your data with transparency and care. This Privacy Policy explains how we collect, use, and safeguard your information.

**Last Updated: June 2024**  
**Effective Date: June 1, 2024**

## 2. Information We Collect

### 2.1 Document Data
- Legal documents uploaded for analysis
- Text content extracted from documents
- Document metadata (file names, timestamps, size)
- Analysis results and generated summaries

### 2.2 User Information
- Account information (if applicable)
- Usage patterns and preferences
- Technical data (IP address, browser type, device information)
- Session duration and feature interaction data

## 3. How We Use Your Information

### 3.1 Primary Purposes
- Providing document analysis and risk assessment services
- Generating summaries and insights from uploaded documents
- Improving our AI algorithms and service accuracy
- Maintaining service security and performance

### 3.2 Legal Basis for Processing
- **Contractual Necessity**: To provide our services
- **Legitimate Interests**: To improve and secure our services
- **Legal Compliance**: To meet regulatory requirements
- **Consent**: For specific data processing activities

## 4. Data Protection Measures

We implement industry-standard security measures including:

- 256-bit SSL/TLS encryption for data transmission
- AES-256 encryption for stored documents
- Regular security audits and penetration testing
- Strict access controls and authentication
- Automated threat detection and prevention

## 5. Data Retention and Deletion

### 5.1 Retention Periods
- Uploaded documents: 30 days from last access
- Analysis results: 60 days from generation

## 6. Your Privacy Rights

Under GDPR and other privacy laws, you have the right to:
- Access your personal data
- Correct inaccurate data
- Request data deletion
- Restrict processing
- Data portability
- Object to processing
- Withdraw consent
- Lodge complaints with supervisory authorities

## 7. International Data Transfers

We may transfer your data to:
- Cloud servers in the EU and US
- AI processing centers in secure locations
- Third-party service providers

All transfers comply with:
- EU Standard Contractual Clauses
- Privacy Shield Framework
- Adequacy decisions where applicable

## 8. Cookie Policy

We use essential cookies for:
- Session management
- Security measures
- Performance monitoring

Optional cookies for:
- Analytics and usage patterns
- Feature preferences
- Service improvements

## 9. Children's Privacy

Our service is not intended for users under 16 years of age. We do not knowingly collect or process data from children.

## 10. Changes to This Policy

We may update this policy to reflect:
- Service changes
- Legal requirements
- Security improvements
- User feedback

All changes will be notified via:
- Email notifications
- In-app announcements
- Website updates

## 11. Contact Information

For privacy-related inquiries:

**Data Protection Officer**  
- Email: privacy@legaldocumentassistant.com  
- Phone: +1 (555) 123-4567  
- Address: 123 Legal Tech Street, Suite 100, San Francisco, CA 94105  

Response Time: Within 48 hours

## 12. Legal Compliance

We comply with:
- General Data Protection Regulation (GDPR)
- California Consumer Privacy Act (CCPA)
- Other applicable data protection laws
"""

def add_privacy_policy_footer():
    """
    Add a minimal privacy policy link and copyright notice to the bottom of the page.
    """
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("View Privacy Policy", key="footer_privacy"):
            st.session_state.show_privacy_policy = True
            st.experimental_rerun()
        
    # Display a copyright notice
    current_year = st.session_state.get('current_year', 2024)
    st.markdown(
        f"""
        <div style="text-align: center; padding: 5px; font-size: 0.8em;">
            © {current_year} AI Legal Document Assistant
        </div>
        """,
        unsafe_allow_html=True
    )

def show_privacy_policy():
    """
    Display the in-app privacy policy with improved styling.
    """
    st.markdown("""
    <style>
    h1, h2, h3 {
        color: #2874A6;
    }
    h1 {
        border-bottom: 2px solid #2874A6;
        padding-bottom: 10px;
    }
    h2 {
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(PRIVACY_POLICY_MARKDOWN)
    
    if st.button("← Back to Application"):
        st.session_state.show_privacy_policy = False
        st.experimental_rerun()

def show_gdpr_info_iframe():
    """
    Show an iframe with external GDPR information.
    """
    st.markdown("### GDPR Information")
    st.markdown("This information is sourced from an external website.")
    
    # Create a responsive iframe using HTML
    st.markdown(
        f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #F0F2F6;">
            <iframe 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
                src="{GDPR_INFO_URL}" 
                title="GDPR Information"
                allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

# Placeholder for GDPR-Compliant Data Handling Functions (TO BE IMPLEMENTED)
# These functions should handle storing, retrieving, deleting, and exporting user data securely.
"""
def store_user_data(user_id, data):
    # Store user data in a GDPR-compliant manner.
    pass

def retrieve_user_data(user_id):
    # Retrieve user data with proper authentication and logging.
    pass

def delete_user_data(user_id):
    # Delete user data upon request (right to be forgotten).
    pass

def export_user_data(user_id):
    # Export user data in a portable format (right to data portability).
    pass
"""
