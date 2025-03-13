import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io
import logging
from fpdf import FPDF
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

class EmailService:
    """Service class for handling email functionality."""
    
    def __init__(self):
        """Initialize the email service."""
        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None
        self._load_email_config()

    def _load_email_config(self):
        """Load email configuration from Streamlit secrets."""
        try:
            self.smtp_server = st.secrets["email"]["SMTP_SERVER"]
            self.smtp_port = int(st.secrets["email"]["SMTP_PORT"])
            self.sender_email = st.secrets["email"]["SENDER_EMAIL"]
            self.sender_password = st.secrets["email"]["SENDER_PASSWORD"]
        except Exception as e:
            logging.error(f"Error loading email configuration: {str(e)}")

    def generate_email_pdf(self, content):
        """Generate a professionally formatted PDF for email attachment"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Add a header with logo placeholder
            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, "Legal Document Analysis", 0, 1, "C")
            pdf.set_font("Arial", "I", 10)
            pdf.cell(190, 5, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
            pdf.line(10, 25, 200, 25)
            pdf.ln(5)
            
            # Process the content by sections
            content_parts = content.split("\n\n")
            
            for part in content_parts:
                if "DOCUMENT SUMMARY" in part:
                    # Summary section
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(190, 10, "Document Summary", 0, 1, "L")
                    pdf.set_font("Arial", "", 11)
                    summary_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part
                    pdf.multi_cell(190, 7, summary_content)
                    pdf.ln(5)
                    
                elif "RISK SCORE" in part:
                    # Risk score section
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(190, 10, "Risk Assessment Score", 0, 1, "L")
                    pdf.set_font("Arial", "", 11)
                    score_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part
                    pdf.multi_cell(190, 7, score_content)
                    pdf.ln(5)
                    
                elif "RISK ANALYSIS" in part:
                    # Risk analysis section
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(190, 10, "Detailed Risk Analysis", 0, 1, "L")
                    pdf.set_font("Arial", "", 11)
                    analysis_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part
                    pdf.multi_cell(190, 7, analysis_content)
                    pdf.ln(5)
                
                else:
                    # Other content
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(190, 7, part)
                    pdf.ln(3)
            
            # Add footer
            pdf.set_y(-15)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 10, f"Page {pdf.page_no()}/{{nb}}", 0, 0, "C")
            
            pdf_bytes = pdf.output(dest="S").encode("latin1")
            buf = io.BytesIO(pdf_bytes)
            buf.seek(0)
            return buf
            
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            return None

    def send_email(self, recipient_email, subject, body, attachment=None, attachment_name=None, attachment_type=None):
        """Send an email with optional attachment."""
        try:
            if not all([self.smtp_server, self.smtp_port, self.sender_email, self.sender_password]):
                return False, "Email configuration is incomplete. Please check your Streamlit secrets."
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment and attachment_name and attachment_type:
                attachment_data = attachment
                
                if attachment_type == "pdf":
                    part = MIMEApplication(attachment_data.read() if hasattr(attachment_data, 'read') else attachment_data, Name=attachment_name)
                    part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                    msg.attach(part)
                elif attachment_type == "docx":
                    part = MIMEApplication(attachment_data.getvalue(), Name=attachment_name)
                    part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                    msg.attach(part)
                elif attachment_type == "txt":
                    part = MIMEText(attachment_data)
                    part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                    msg.attach(part)
                    
            # Connect to server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            return True, "Email sent successfully!"
            
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return False, f"Error sending email: {str(e)}"

    @staticmethod
    def validate_email(email):
        """Simple email validation"""
        if not email:
            return False
        if "@" not in email or "." not in email:
            return False
        return True

    def prepare_email_content(self, include_summary, include_risk_score, include_risks, include_visuals):
        """Prepare well-formatted content for email"""
        email_content = []
        
        # Add document summary if selected
        if include_summary and st.session_state.get("summary"):
            email_content.append("DOCUMENT SUMMARY")
            email_content.append("-" * 30)
            
            summary = st.session_state.summary
            # Format summary if needed (e.g., bullet points)
            if not summary.startswith("•") and not summary.startswith("-"):
                paragraphs = [p.strip() for p in summary.split("\n") if p.strip()]
                formatted_summary = "\n\n".join(paragraphs)
                email_content.append(formatted_summary)
            else:
                email_content.append(summary)
        
        # Add risk score if selected
        if include_risk_score and st.session_state.get("risks"):
            email_content.append("\nRISK SCORE")
            email_content.append("-" * 30)
            
            if isinstance(st.session_state.risks, str):
                score, high, medium, low = self._calculate_risk_counts(st.session_state.risks)
                
                email_content.append(f"Overall Risk Score: {score}/100")
                email_content.append(f"Risk Level: {'High' if score >= 70 else 'Medium' if score >= 40 else 'Low'}")
                email_content.append(f"High Priority Issues: {high}")
                email_content.append(f"Medium Priority Issues: {medium}")
                email_content.append(f"Low Priority Issues: {low}")
            else:
                email_content.append("Risk score analysis is included in the detailed risk section.")
        
        # Add risk analysis if selected
        if include_risks and st.session_state.get("risks"):
            email_content.append("\nRISK ANALYSIS")
            email_content.append("-" * 30)
            
            if isinstance(st.session_state.risks, str):
                risks_text = st.session_state.risks
                high_risks, medium_risks, low_risks = self._categorize_risks(risks_text)
                
                if high_risks:
                    email_content.append("\nHIGH PRIORITY RISKS:")
                    for i, risk in enumerate(high_risks, 1):
                        email_content.append(f"{i}. {risk}")
                
                if medium_risks:
                    email_content.append("\nMEDIUM PRIORITY RISKS:")
                    for i, risk in enumerate(medium_risks, 1):
                        email_content.append(f"{i}. {risk}")
                
                if low_risks:
                    email_content.append("\nLOW PRIORITY RISKS:")
                    for i, risk in enumerate(low_risks, 1):
                        email_content.append(f"{i}. {risk}")
                    
                if not (high_risks or medium_risks or low_risks):
                    email_content.append(risks_text)
            else:
                email_content.append("Detailed risk analysis is not available in text format.")
        
        return "\n\n".join(email_content)

    def _calculate_risk_counts(self, risks_text):
        """Calculate risk counts and score from text"""
        text_lower = risks_text.lower()
        
        # Count risk keywords
        high_count = sum(text_lower.count(word) for word in ['critical', 'severe', 'high risk', 'significant'])
        medium_count = sum(text_lower.count(word) for word in ['moderate', 'medium', 'potential', 'possible'])
        low_count = len(text_lower.split('.')) - high_count - medium_count
        low_count = max(0, low_count)
        
        # Calculate score
        total = high_count + medium_count + low_count
        if total == 0:
            return 0, 0, 0, 0
            
        score = min(100, round((high_count * 3 + medium_count * 2 + low_count) / total * 20))
        return score, high_count, medium_count, low_count

    def _categorize_risks(self, risks_text):
        """Categorize risks by severity"""
        sentences = [s.strip() for s in risks_text.split('.') if s.strip()]
        
        high_risks = []
        medium_risks = []
        low_risks = []
        
        high_keywords = ['critical', 'severe', 'high risk', 'significant']
        medium_keywords = ['moderate', 'medium', 'potential', 'possible']
        
        for sentence in sentences:
            lower_sentence = sentence.lower()
            if any(keyword in lower_sentence for keyword in high_keywords):
                high_risks.append(sentence)
            elif any(keyword in lower_sentence for keyword in medium_keywords):
                medium_risks.append(sentence)
            else:
                low_risks.append(sentence)
                
        return high_risks, medium_risks, low_risks

def email_ui_section():
    """Display the email UI section in the Streamlit app."""
    st.subheader("📧 Email Results")
    
    email_service = EmailService()
    
    recipient_email = st.text_input("Recipient Email Address")
    
    if recipient_email and not email_service.validate_email(recipient_email):
        st.error("Please enter a valid email address")
        return
        
    # Content selection
    st.write("Select content to include:")
    include_summary = st.checkbox("Include Document Summary", value=True)
    include_risk_score = st.checkbox("Include Risk Score", value=True)
    include_risks = st.checkbox("Include Detailed Risk Analysis", value=True)
    include_visuals = st.checkbox("Include Visualizations", value=False)
    
    # Format selection
    format_options = ["PDF", "DOCX", "TXT"]
    selected_format = st.selectbox("Select Export Format", format_options)
    
    if st.button("Send Email"):
        if not recipient_email:
            st.error("Please enter a recipient email address")
            return
            
        with st.spinner("Preparing and sending email..."):
            # Prepare email content
            email_content = email_service.prepare_email_content(
                include_summary,
                include_risk_score,
                include_risks,
                include_visuals
            )
            
            # Prepare attachment based on selected format
            attachment = None
            attachment_name = None
            attachment_type = None
            
            if selected_format == "PDF":
                attachment = email_service.generate_email_pdf(email_content)
                attachment_name = "legal_analysis.pdf"
                attachment_type = "pdf"
            elif selected_format == "DOCX":
                # Add DOCX generation logic here
                pass
            elif selected_format == "TXT":
                attachment = email_content
                attachment_name = "legal_analysis.txt"
                attachment_type = "txt"
            
            # Send email
            success, message = email_service.send_email(
                recipient_email,
                "Legal Document Analysis Results",
                "Please find attached the legal document analysis results.",
                attachment,
                attachment_name,
                attachment_type
            )
            
            if success:
                st.success(message)
            else:
                st.error(message) 