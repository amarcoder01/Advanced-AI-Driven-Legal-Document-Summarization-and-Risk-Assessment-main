import streamlit as st
import os
import json
from datetime import datetime
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIVACY_POLICY_FILE = "privacy_policy.html"
PRIVACY_POLICY_PATH = os.path.join(os.getcwd(), PRIVACY_POLICY_FILE)
GDPR_INFO_URL = "https://gdpr-info.eu/"
DATA_STORAGE_PATH = os.path.join(os.getcwd(), "user_data")

os.makedirs(DATA_STORAGE_PATH, exist_ok=True)

PRIVACY_POLICY_MARKDOWN = """
# Privacy Policy

## 1. Overview

Welcome to AI Legal Document Assistant. We are committed to protecting your privacy and handling your data with transparency and care. This Privacy Policy explains how we collect, use, and safeguard your information.

**Last Updated: March 2025**  
**Effective Date: March 10, 2025**

## 2. Information We Collect

### 2.1 Document Data
* Legal documents uploaded for analysis
* Text content extracted from documents
* Document metadata (file names, timestamps, size)
* Analysis results and generated summaries

### 2.2 User Information
* Account information (if applicable)
* Usage patterns and preferences
* Technical data (IP address, browser type, device information)
* Session duration and feature interaction data

## 3. How We Use Your Information

### 3.1 Primary Purposes
* Providing document analysis and risk assessment services
* Generating summaries and insights from uploaded documents
* Improving our AI algorithms and service accuracy
* Maintaining service security and performance

### 3.2 Legal Basis for Processing
* **Contractual Necessity**: To provide our services
* **Legitimate Interests**: To improve and secure our services
* **Legal Compliance**: To meet regulatory requirements
* **Consent**: For specific data processing activities

## 4. Data Protection Measures

We implement industry-standard security measures including:

* 256-bit SSL/TLS encryption for data transmission
* AES-256 encryption for stored documents
* Regular security audits and penetration testing
* Strict access controls and authentication
* Automated threat detection and prevention

## 5. Data Retention and Deletion

### 5.1 Retention Periods
* Uploaded documents: 30 days from last access
* Analysis results: 60 days from generation
* Account information: Duration of account activity
* Usage logs: 90 days rolling period

### 5.2 Automatic Deletion
* Documents are automatically deleted after the retention period
* Users can request immediate deletion at any time
* Backup copies are removed within 30 days of deletion

## 6. Your Privacy Rights

Under GDPR and other privacy laws, you have the right to:

* Access your personal data
* Correct inaccurate data
* Request data deletion
* Restrict processing
* Data portability
* Object to processing
* Withdraw consent
* Lodge complaints with supervisory authorities

## 7. International Data Transfers

We may transfer your data to:

* Cloud servers in the EU and US
* AI processing centers in secure locations
* Third-party service providers

All transfers comply with:
* EU Standard Contractual Clauses
* Privacy Shield Framework
* Adequacy decisions where applicable

## 8. Cookie Policy

We use essential cookies for:
* Session management
* Security measures
* Performance monitoring

Optional cookies for:
* Analytics and usage patterns
* Feature preferences
* Service improvements

## 9. Children's Privacy

Our service is not intended for users under 16 years of age. We do not knowingly collect or process data from children.

## 10. Changes to This Policy

We may update this policy to reflect:
* Service changes
* Legal requirements
* Security improvements
* User feedback

All changes will be notified via:
* Email notifications
* In-app announcements
* Website updates

## 11. Contact Information

For privacy-related inquiries:

**Data Protection Officer**
* Email: privacy@legaldocumentassistant.com
* Phone: +1 (555) 123-4567
* Address: 123 Legal Tech Street, Suite 100, San Francisco, CA 94105

Response Time: Within 48 hours

## 12. Legal Compliance

We comply with:
- General Data Protection Regulation (GDPR)
- California Consumer Privacy Act (CCPA)
- Other applicable data protection laws

---

© 2025 VidzAI. All rights reserved.
This software and associated documentation files are the property of VidzAI.
No part of this software may be copied, modified, distributed, or used without explicit permission from VidzAI.
"""

def add_privacy_policy_footer():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("View Privacy Policy", key="footer_privacy"):
            st.session_state.show_privacy_policy = True
            st.experimental_rerun()
    current_year = st.session_state.get('current_year', 2025)
    st.markdown(
        f"""
        <div style="text-align: center; padding: 5px; font-size: 0.8em;">
            © {current_year} VidzAI - AI Legal Document Assistant<br>
            All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

def show_privacy_policy():
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
    .footer {
        text-align: center;
        font-size: 0.8em;
        margin-top: 30px;
        border-top: 2px solid #2874A6;
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(PRIVACY_POLICY_MARKDOWN)
    
    if st.button("← Back to Application"):
        st.session_state.show_privacy_policy = False
        st.experimental_rerun()

def show_gdpr_info_iframe():
    st.markdown("### GDPR Information")
    st.markdown("This information is sourced from an external website.")
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

def show_gdpr_consent_banner():
    if 'gdpr_consent' not in st.session_state:
        st.session_state.gdpr_consent = False
    if not st.session_state.gdpr_consent:
        with st.container():
            st.markdown("""
            <div style='position: fixed; bottom: 0; left: 0; right: 0; background-color: #F8F9F9; 
                        padding: 20px; border-top: 4px solid #2874A6; z-index: 1000;'>
                <h4 style='color: #2874A6;'>🔒 Privacy & Cookies Notice</h4>
                <p>We use cookies and process your data to provide our services. By using this application, 
                   you agree to our Privacy Policy and data processing practices.</p>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                if st.button("View Privacy Policy", key="consent_privacy"):
                    st.session_state.show_privacy_policy = True
                    st.experimental_rerun()
            with col3:
                if st.button("Accept", key="consent_accept", type="primary"):
                    st.session_state.gdpr_consent = True
                    st.experimental_rerun()

def store_user_data(user_id: str, data: Dict[str, Any]) -> bool:
    try:
        file_path = os.path.join(DATA_STORAGE_PATH, f"{user_id}.json")
        data['last_updated'] = datetime.now().isoformat()
        data['retention_period'] = '30 days'
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data stored successfully for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing data for user {user_id}: {str(e)}")
        return False

def retrieve_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    try:
        file_path = os.path.join(DATA_STORAGE_PATH, f"{user_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Data retrieved successfully for user {user_id}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving data for user {user_id}: {str(e)}")
        return None

def delete_user_data(user_id: str) -> bool:
    try:
        file_path = os.path.join(DATA_STORAGE_PATH, f"{user_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Data deleted successfully for user {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting data for user {user_id}: {str(e)}")
        return False

def export_user_data(user_id: str) -> Optional[str]:
    try:
        data = retrieve_user_data(user_id)
        if data:
            export_data = {
                'user_id': user_id,
                'data': data,
                'export_date': datetime.now().isoformat(),
                'data_controller': 'VidzAI Legal Document Assistant'
            }
            logger.info(f"Data exported successfully for user {user_id}")
            return json.dumps(export_data, indent=4)
        return None
    except Exception as e:
        logger.error(f"Error exporting data for user {user_id}: {str(e)}")
        return None
